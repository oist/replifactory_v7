#!/usr/bin/env python
import os

from ._version import get_data as get_version_data


def get_version():
    version_from_file = get_version_from_file()
    if version_from_file:
        return version_from_file
    else:
        from setuptools_scm import get_version

        version = get_version(root="..", relative_to=__file__)
        return version


def get_version_from_file():
    vf = version_file()
    if vf:
        with open(vf, "r") as file:
            return file.read().strip()


def version_file():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(current_dir, "..", "VERSION")

    if os.path.exists(version_file):
        return version_file


try:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("biofactory").version
except pkg_resources.DistributionNotFound:
    __version__ = get_version()

__all__ = ["__version__"]

# version_data = get_version_data()

# __version__ = version_data["version"]
# __version__ = "0.0.1.dev254+3342b9d"
# __branch__ = version_data["branch"]
__display_version__ = __version__
# __revision__ = version_data["revision"]

# del version_data
del get_version_data


def main():
    import sys

    # os args are gained differently on win32
    try:
        from click.utils import get_os_args

        args = get_os_args()
    except ImportError:
        # for whatever reason we are running an older Click version?
        args = sys.argv[1:]

    if len(args) >= len(sys.argv):
        # Now some ugly preprocessing of our arguments starts. We have a somewhat difficult situation on our hands
        # here if we are running under Windows and want to be able to handle utf-8 command line parameters (think
        # plugin parameters such as names or something, e.g. for the "dev plugin:new" command) while at the same
        # time also supporting sys.argv rewriting for debuggers etc (e.g. PyCharm).
        #
        # So what we try to do here is solve this... Generally speaking, sys.argv and whatever Windows returns
        # for its CommandLineToArgvW win32 function should have the same length. If it doesn't however and
        # sys.argv is shorter than the win32 specific command line arguments, obviously stuff was cut off from
        # sys.argv which also needs to be cut off of the win32 command line arguments.
        #
        # So this is what we do here.

        # -1 because first entry is the script that was called
        sys_args_length = len(sys.argv) - 1

        # cut off stuff from the beginning
        args = args[-1 * sys_args_length :] if sys_args_length else []

    from biofactory.app import main

    main(args=args, prog_name="biofactory", auto_envvar_prefix="BIOFACTORY")


if __name__ == "__main__":
    main()
