"""I'm throwing this in because it is often useful in testing.
"""

import os
import shutil
import testfixtures


def force_permissions(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o777)
        for f in files:
            os.chmod(os.path.join(root, f), 0o777)


def rmtree_forcing_permissions(dir_path):
    force_permissions(dir_path)
    shutil.rmtree(dir_path)


class TempDirMaker(object):

    def __init__(self, add_cleanup):
        self._add_cleanup = add_cleanup

    def make_temp_dir(self, rmtree):
        d = testfixtures.TempDirectory()

        if rmtree is None:
            remove = d.cleanup
        else:
            def remove():
                rmtree(d.path)
                d.instances.remove(d)  # silence warning

        def remove_directory():
            # TempDirectory.cleanup() fails if file permissions don't allow
            # removing
            try:
                remove()
            except PermissionError:
                print("Failed to clean up {}".format(d.path))
                raise
        self._add_cleanup(remove_directory)
        return d.path
