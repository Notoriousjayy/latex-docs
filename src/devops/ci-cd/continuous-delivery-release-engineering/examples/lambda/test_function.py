import json
import unittest
from function import handler

class HandlerTests(unittest.TestCase):
    def test_health(self):
        actual = handler({"rawPath": "/health"}, None)
        self.assertEqual(actual["statusCode"], 200)
        self.assertEqual(json.loads(actual["body"])["status"], "ok")

    def test_unknown_path(self):
        actual = handler({"rawPath": "/missing"}, None)
        self.assertEqual(actual["statusCode"], 404)

    def test_non_mapping_event(self):
        self.assertEqual(handler(None, None)["statusCode"], 200)

if __name__ == "__main__":
    unittest.main()
