from lib import monkeypatch

from unittest import TestCase


class TestAddToList(TestCase):

    def make_dirty_patcher(self):
        return monkeypatch.MonkeyPatcher(add_cleanup=lambda f: None)

    def test_add_to_list_adds_to_list(self):
        patcher = self.make_dirty_patcher()
        l = [1, 2]
        patcher.add_to_list(l, 3)
        self.assertEqual(l, [1, 2, 3])

    def test_add_to_list_does_not_add_twice(self):
        patcher = self.make_dirty_patcher()
        l = [1, 2]
        patcher.add_to_list(l, 1)
        self.assertEqual(l, [1, 2])
        patcher.add_to_list(l, 2)
        self.assertEqual(l, [1, 2])

    def test_add_to_list_gets_reverted(self):
        cleanups = []
        patcher = monkeypatch.MonkeyPatcher(add_cleanup=cleanups.append)
        l = [1, 2]
        patcher.add_to_list(l, 3)
        self.assertEqual(l, [1, 2, 3])
        [cleanup] = cleanups
        cleanup()
        self.assertEqual(l, [1, 2])

    def test_add_to_list_does_not_get_reverted_if_was_there_before(self):
        cleanups = []
        patcher = monkeypatch.MonkeyPatcher(add_cleanup=cleanups.append)
        l = [1, 2]
        patcher.add_to_list(l, 2)
        self.assertEqual(l, [1, 2])
        self.assertEqual(len(cleanups), 0)
