#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from setuptools import PEP420PackageFinder, setup

from scripts.include import (get_files, get_git_date_and_time, get_git_version,
                             git_check_tag_for_HEAD)

find_namespace_packages = PEP420PackageFinder.find

THIS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))

package_version = [0, 8, 2]
data_files = {
    "/etc/covscan": [
        "osh/client/covscan.conf",
        "osh/worker/covscand.conf",
        "osh/worker/covscand.conf.prod",
        "osh/worker/covscand.conf.stage",
    ],
    "/etc/httpd/conf.d": [
        "covscanhub/covscanhub-httpd.conf.prod",
        "covscanhub/covscanhub-httpd.conf.stage",
    ],
    "/usr/lib/systemd/system": [
        "files/etc/systemd/system/covscand.service",
    ],
    "/etc/bash_completion.d": [
        "files/etc/bash_completion.d/covscan.bash",
    ],
    "/usr/bin": [
        "osh/client/covscan",
    ],
    "/usr/sbin": [
        "osh/worker/covscand",
    ],
}
package_data = {
    "covscanhub": [
        "covscanhub.wsgi",
        "scripts/checker_groups.txt",
    ]
}

for folder in (
    "static",
    "templates",
    "media",
    "scan/fixtures",
    "errata/fixtures",
    "fixtures",
):
    package_data["covscanhub"].extend(get_files("covscanhub", folder))

if os.path.isdir(".git"):
    if not git_check_tag_for_HEAD(THIS_FILE_PATH):
        package_version.append("git")
        git_version = get_git_version(THIS_FILE_PATH)
        git_date, git_time = get_git_date_and_time(THIS_FILE_PATH)
        package_version += [git_date, git_time, git_version]

setup(
    name="covscan",
    version=".".join(map(str, package_version)),
    url="https://gitlab.cee.redhat.com/covscan/covscan",
    author="Red Hat, Inc.",
    author_email="ttomecek@redhat.com",
    description="Coverity scan scheduler",
    # This expects `kobo` directory does not exist under current directory
    # TODO: How to exclude `kobo` directory?
    packages=find_namespace_packages(),
    package_data=package_data,
    data_files=data_files.items(),
)
