import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from unittest import mock


SSHBOX_PATH = Path(__file__).resolve().parents[1] / "sshbox"


def load_sshbox_module() -> ModuleType:
    loader = SourceFileLoader("sshbox_module", str(SSHBOX_PATH))
    module = ModuleType(loader.name)
    module.__file__ = str(SSHBOX_PATH)
    loader.exec_module(module)
    return module


class SelectPubKeyPathTests(unittest.TestCase):
    def test_prefers_ed25519_pub_then_rsa_pub(self):
        sshbox = load_sshbox_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            ssh_dir = home / ".ssh"
            ssh_dir.mkdir()
            rsa_key = ssh_dir / "id_rsa.pub"
            rsa_key.write_text("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD test\n")

            with mock.patch.object(sshbox.Path, "home", return_value=home):
                selected = sshbox.select_public_key_path(None)

            self.assertEqual(selected, rsa_key)

            ed25519_key = ssh_dir / "id_ed25519.pub"
            ed25519_key.write_text("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI test\n")

            with mock.patch.object(sshbox.Path, "home", return_value=home):
                selected = sshbox.select_public_key_path(None)

            self.assertEqual(selected, ed25519_key)

    def test_rejects_when_no_default_public_key_exists(self):
        sshbox = load_sshbox_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            (home / ".ssh").mkdir()

            with mock.patch.object(sshbox.Path, "home", return_value=home):
                with self.assertRaises(SystemExit) as exc:
                    sshbox.select_public_key_path(None)

        self.assertEqual(exc.exception.code, 1)

    def test_accepts_explicit_public_key_path(self):
        sshbox = load_sshbox_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            pubkey = Path(temp_dir) / "custom.pub"
            pubkey.write_text("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI custom\n")

            selected = sshbox.select_public_key_path(str(pubkey))

        self.assertEqual(selected, pubkey)


class UsageTests(unittest.TestCase):
    def test_print_usage_mentions_push_ssh_pub(self):
        sshbox = load_sshbox_module()
        with mock.patch("builtins.print") as print_mock:
            sshbox.print_usage()

        printed = "\n".join(call.args[0] for call in print_mock.call_args_list)
        self.assertIn("sshbox push-ssh-pub <name> [pubkey_path]", printed)


class PushSshPubCommandTests(unittest.TestCase):
    def test_push_ssh_pub_expect_script_passes_remote_command_directly(self):
        sshbox = load_sshbox_module()
        self.assertIn("spawn ssh -o ServerAliveInterval=30", sshbox.PUSH_SSH_PUB_EXPECT_SCRIPT)
        self.assertIn("-p $port $target $remote_command", sshbox.PUSH_SSH_PUB_EXPECT_SCRIPT)
        self.assertNotIn("sh -c $remote_command", sshbox.PUSH_SSH_PUB_EXPECT_SCRIPT)

    def test_cmd_push_ssh_pub_passes_public_key_to_run_expect(self):
        sshbox = load_sshbox_module()
        server = {
            "name": "prod",
            "host": "example.com",
            "port": 22,
            "user": "root",
            "comment": "",
            "password": "secret",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            pubkey = Path(temp_dir) / "id_ed25519.pub"
            key_line = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI pushed-key comment"
            pubkey.write_text(key_line + "\n")

            with (
                mock.patch.object(sshbox, "find_server", return_value=server),
                mock.patch.object(sshbox, "require_command"),
                mock.patch.object(sshbox, "run_expect", return_value=0) as run_expect_mock,
            ):
                result = sshbox.cmd_push_ssh_pub("prod", str(pubkey))

        self.assertEqual(result, 0)
        run_expect_mock.assert_called_once()
        _, _, command, extra_env = run_expect_mock.call_args.args
        self.assertEqual(command, ["expect", "-c", sshbox.PUSH_SSH_PUB_EXPECT_SCRIPT])
        self.assertEqual(extra_env["SSHBOX_PUBKEY"], key_line)
        self.assertIn("authorized_keys", extra_env["SSHBOX_REMOTE_COMMAND"])


if __name__ == "__main__":
    unittest.main()
