# -*- coding: utf-8 -*-


import os
import re

from django.core.exceptions import ObjectDoesNotExist

import koji

from kobo.hub.models import Task, TASK_STATES
from kobo.django.upload.models import FileUpload
from kobo.django.xmlrpc.decorators import login_required, admin_required

from covscanhub.scan.models import MockConfig, Package, Tag, TaskExtension
from covscanhub.scan.service import create_diff_task
from covscanhub.errata.service import create_errata_base_scan


__all__ = (
    "diff_build",
    "mock_build",
    "create_user_diff_task",
    "create_base_scans",
)


class DiffBuild(object):
    def __init__(self, koji_url):
        self.koji_url = koji_url
        self.koji_proxy = koji.ClientSession(self.koji_url)

    def get_task_class_name(self):
        return "DiffBuild"

    def __call__(self, request, mock_config, comment=None, options=None):
        """
            @param mock_config: mock config name
            @type  mock_config: str
            @param comment: scan description
            @type  comment: str
            @param options:
            @type  options: dict
        """
        comment = comment or ""
        options = options or {}

        upload_id = options.pop("upload_id", None)
        brew_build = options.pop("brew_build", None)

        if upload_id is None and brew_build is None:
            raise RuntimeError("Neither upload_id or brew_build specified.")
        if upload_id is not None and brew_build is not None:
            raise RuntimeError("Can't specify both upload_id and brew_build at the same time.")

        priority = options.pop("priority", 10)
        if priority is not None:
            max_prio = 20
            if int(priority) > max_prio and not request.user.is_superuser:
                raise RuntimeError("Setting high task priority (>%s) requires admin privileges." % max_prio)

        try:
            conf = MockConfig.objects.get(name=mock_config)
        except:
            raise ObjectDoesNotExist("Unknown mock config: %s" % mock_config)
        if not conf.enabled:
            raise RuntimeError("Mock config is disabled: %s" % mock_config)
        options["mock_config"] = mock_config

        if upload_id:
            try:
                upload = FileUpload.objects.get(id=upload_id)
            except:
                raise ObjectDoesNotExist("Can't find uploaded file with id: %s" % upload_id)

            if upload.owner.username != request.user.username:
                raise RuntimeError("Can't process a file uploaded by a different user")

            srpm_path = os.path.join(upload.target_dir, upload.name)
            options["srpm_name"] = upload.name
            task_label = options["srpm_name"]

        if brew_build:
            options["brew_build"] = brew_build
            task_label = options["brew_build"]

        # remove sensitive data from options['CIM'] if they exists
        cim_conf = options.pop("CIM", None)

        task_id = Task.create_task(request.user.username, task_label, self.get_task_class_name(), options, comment=comment, state=TASK_STATES["CREATED"], priority=priority)
        task_dir = Task.get_task_dir(task_id)

        task = Task.objects.get(id=task_id)

        # check CIM settings
        if cim_conf:
            TaskExtension(task=task, secret_args=cim_conf).save()

        if not os.path.isdir(task_dir):
            try:
                os.makedirs(task_dir, mode=0755)
            except OSError, ex:
                if ex.errno != 17:
                    raise

        if upload_id:
            # move file to task dir, remove upload record and make the task available
            import shutil
            shutil.move(srpm_path, os.path.join(task_dir, os.path.basename(srpm_path)))
            upload.delete()

        # set the task state to FREE
        task.free_task()
        return task_id


class MockBuild(DiffBuild):
    def get_task_class_name(self):
        return "MockBuild"


diff_build_obj = DiffBuild("http://brewhub.devel.redhat.com/brewhub")
mock_build_obj = MockBuild("http://brewhub.devel.redhat.com/brewhub")


@login_required
def diff_build(*args, **kwargs):
    global diff_build_obj
    return diff_build_obj(*args, **kwargs)


@login_required
def mock_build(*args, **kwargs):
    global mock_build_obj
    return mock_build_obj(*args, **kwargs)


@login_required
def create_user_diff_task(request, kwargs):
    """
        create scan of a package and perform diff on results against specified
        version

        kwargs:
         - nvr_srpm - name, version, release of scanned package
         - nvr_upload_id - upload id for target, so worker is able to download it
         - nvr_brew_build - NVR of package to be downloaded from brew
         - base_srpm - name, version, release of base package
         - base_upload_id - upload id for base, so worker is able to download it
         - base_brew_build - NVR of base package to be downloaded from brew
         - nvr_mock - mock config
         - base_mock - mock config
    """
    kwargs['task_user'] = request.user.username
    return create_diff_task(kwargs)


@admin_required
def create_base_scans(request, nvrs_list, tag_name):
    try:
        tag = Tag.objects.get(name=tag_name)
    except ObjectDoesNotExist:
        return ['Tag %s does not exist' % tag_name]
    response = []
    nvr_pattern = re.compile("(.*)-(.*)-(.*)")
    for nvr in nvrs_list:
        m = nvr_pattern.match(nvr)
        if m:
            package_str = m.group(1)
            package, created = Package.objects.get_or_create(name=package_str)
            if not created and package.blocked:
                response.append('package %s is blacklisted' % package_str)
            options = {
                'username': request.user.username,
                'task_user': request.user.username,
                'base': nvr,
                'base_tag': tag_name,
                'nvr': 'prescan',
            }
            create_errata_base_scan(options, None, package)
        else:
            response.append('%s is not a valid NVR' % nvr)
    return response