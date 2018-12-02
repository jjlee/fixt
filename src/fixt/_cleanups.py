import logging
import unittest


logger = logging.getLogger(__name__)


class FailedToCleanUpError(Exception):

    pass


class Cleanups:

    def __init__(self):
        self._cleanups = []

    def add_cleanup(self, func):
        self._cleanups.append(func)

    def clean_up(self):
        success = True
        for func in reversed(self._cleanups):
            try:
                func()
            except:
                success = False
                logger.exception('Error in cleanup function %s', func)
        if not success:
            raise FailedToCleanUpError()


class CleanupMixin:

    """For contexts tests."""

    def given_cleanups(self):
        self.cleanups = Cleanups()

    def cleanup(self):
        self.cleanups.clean_up()

    def add_cleanup(self, func):
        self.cleanups.add_cleanup(func)


class PytestCleanupBase(unittest.TestCase):

    # As far as I know, pytest doesn't provide a way to execute tear down
    # functions (the feature it calls "addfinalizer") without either use of its
    # fixtures framework or inheriting from unittest.TestCase.

    # Inheriting isn't so bad here, because I don't use inheritance much, so
    # its use here does not conflict with other inheritance requirements.  In
    # code that separate fixtures from tests, such as fixt or (somewhat) pytest
    # fixtures, there is less need for inheritance.

    # I tried setup_method, but it seems that does not support inheritance
    # (doesn't seem to be defined in the docs), so I'm not using that.  Why,
    # given I don't use inheritance much?  I do use it occasionally, in
    # particular to add helper methods to the class.  Of course, those can also
    # be written instead as fixt fixtures that return closures.

    def setUp(self):
        super().setUp()
        self.cleanups = Cleanups()

    def tearDown(self):
        super().tearDown()
        self.cleanups.clean_up()

    def add_cleanup(self, func):
        self.cleanups.add_cleanup(func)
