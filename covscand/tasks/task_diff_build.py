# -*- coding: utf-8 -*-


import os
import sys
import grp
import pipes
import shutil
import tempfile
import urllib

from kobo.rpmlib import get_rpm_header
from kobo.shortcuts import run
from kobo.worker import TaskBase


class DiffBuild(TaskBase):
    enabled = True

    arches = ["noarch"]    # list of supported architectures
    channels = ["default"] # list of channels
    exclusive = False      # leave False here unless you really know what you're doing
    foreground = False     # if True the task is not forked and runs in the worker process (no matter you run worker without -f)
    priority = 19
    weight = 1.0

    def run(self):
        mock_config = self.args.pop("mock_config")
        srpm_name = self.args.pop("srpm_name")
        keep_covdata = self.args.pop("keep_covdata")

        # create a temp dir, make it writable by 'coverity' user
        tmp_dir = tempfile.mkdtemp(prefix="covscan_")
        os.chmod(tmp_dir, 0775)
        coverity_gid = grp.getgrnam("coverity").gr_gid
        os.chown(tmp_dir, -1, coverity_gid)

        # download SRPM
        task_url = self.hub.client.task_url(self.task_id).rstrip("/")
        srpm_path = os.path.join(tmp_dir, srpm_name)
        urllib.urlretrieve("%s/log/%s?format=raw" % (task_url, srpm_name), srpm_path)

        try:
            get_rpm_header(srpm_path)
        except:
            import kobo.tback
            print >> sys.stderr, "Invalid RPM file(%s): %s" % (srpm_name, kobo.tback.get_exception())
            self.fail()

        keep_covdata_option = keep_covdata and "-i" or ""
        cmd = pipes.quote("cd %s; cov-diffbuild %s %s %s" % (tmp_dir, keep_covdata_option, mock_config, srpm_path))
        retcode, output = run("su - coverity -c %s" % cmd, can_fail=True, stdout=True)
        if retcode:
            self.fail()

        # upload results back to hub
        xz_path = srpm_path[:-8] + ".tar.xz"
        if not os.path.exists(xz_path):
            xz_path = srpm_path[:-8] + ".tar.lzma"
        self.hub.upload_task_log(open(xz_path), self.task_id, os.path.basename(xz_path))

        # remove temp files
        shutil.rmtree(tmp_dir)

    @classmethod
    def cleanup(cls, hub, conf, task_info):
        pass
        # remove temp files, etc.

    @classmethod
    def notification(cls, hub, conf, task_info):
        hub.worker.email_task_notification(task_info["id"])
