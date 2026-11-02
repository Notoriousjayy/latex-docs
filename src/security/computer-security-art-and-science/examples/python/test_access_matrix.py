import unittest
from access_matrix import AccessMatrix


class AccessMatrixTests(unittest.TestCase):
    def setUp(self):
        self.matrix = AccessMatrix({"report": "alice"})

    def test_default_deny(self):
        self.assertFalse(self.matrix.check("bob", "report", "read"))

    def test_owner_grants_and_revokes(self):
        self.matrix.grant("alice", "bob", "report", "read")
        self.assertTrue(self.matrix.check("bob", "report", "read"))
        self.assertFalse(self.matrix.check("bob", "report", "write"))
        self.matrix.revoke("alice", "bob", "report", "read")
        self.assertFalse(self.matrix.check("bob", "report", "read"))

    def test_subject_cannot_escalate_privilege(self):
        with self.assertRaises(PermissionError):
            self.matrix.grant("bob", "bob", "report", "write")
        self.assertFalse(self.matrix.check("bob", "report", "write"))

    def test_invalid_right_is_rejected(self):
        with self.assertRaises(PermissionError):
            self.matrix.grant("alice", "bob", "report", "own")


if __name__ == "__main__":
    unittest.main()
