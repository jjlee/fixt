"""I'm throwing this in because it is often useful in testing.
"""

import testfixtures


class TempDirMaker(object):

    def __init__(self, add_cleanup):
        self._add_cleanup = add_cleanup

    def make_temp_dir(self):
        d = testfixtures.TempDirectory()

        def remove_directory():
            d.cleanup()
        self._add_cleanup(remove_directory)
        return d.path
