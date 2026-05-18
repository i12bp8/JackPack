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

    def test_select_interface_becomes_headless_env_field(self):
        schema = web_server._payload_form_schema(Path("payloads/wifi/deauth.py"))
        first = schema["fields"][0]

        self.assertEqual(first["env"], "JACKPACK_SELECTED_IFACE")
        self.assertEqual(first["type"], "interface")
        self.assertEqual(first["iface_type"], "wifi")

    def test_payload_schema_has_runtime_actions(self):
        schema = web_server._payload_form_schema(Path("payloads/wifi/deauth.py"))
        buttons = {action["button"] for action in schema["actions"]}

        self.assertIn("OK", buttons)
        self.assertIn("KEY3", buttons)

    def test_wifi_security_key_mgmt_prefers_wpa2_for_transition_networks(self):
        self.assertEqual(web_server._security_key_mgmt("WPA2", "secret"), "wpa-psk")
        self.assertEqual(web_server._security_key_mgmt("WPA2 WPA3", "secret"), "wpa-psk")
        self.assertEqual(web_server._security_key_mgmt("WPA3 SAE", "secret"), "sae")

    def test_diagnostics_shape(self):
        data = web_server._system_diagnostics()

        self.assertTrue(data["ok"])
        self.assertIn("counts", data)
        self.assertIn("checks", data)
        self.assertTrue(any(check["key"] == "git_origin" for check in data["checks"]))


if __name__ == "__main__":
    unittest.main()
