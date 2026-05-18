import unittest
from pathlib import Path

import web_server


class PayloadFormSchemaTests(unittest.TestCase):
    def test_argparse_choices_from_static_dict_keys(self):
        schema = web_server._payload_form_schema(Path("payloads/reconnaissance/honeypot.py"))
        fields = {field["name"]: field for field in schema["fields"]}

        self.assertEqual(schema["mode"], "form")
        self.assertEqual(fields["profile"]["type"], "select")
        self.assertIn("basic", fields["profile"]["choices"])
        self.assertEqual(fields["os_profile"]["type"], "select")
        self.assertIn("ubuntu22", fields["os_profile"]["choices"])

    def test_diagnostics_shape(self):
        data = web_server._system_diagnostics()

        self.assertTrue(data["ok"])
        self.assertIn("counts", data)
        self.assertIn("checks", data)
        self.assertTrue(any(check["key"] == "git_origin" for check in data["checks"]))


if __name__ == "__main__":
    unittest.main()
