import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/theoryxu/IdeaProjects/sshbox")
DEPLOY_SCRIPT = REPO_ROOT / "deploy.sh"
EXPECTED_SERVERS_TEMPLATE = """[
  {
    "name": "prod",
    "host": "192.168.1.10",
    "port": 22,
    "user": "root",
    "comment": "Production",
    "password": "replace-me"
  },
  {
    "name": "test",
    "host": "10.0.0.8",
    "port": 2222,
    "user": "ubuntu",
    "comment": "Testing",
    "password": "replace-me-too"
  }
]
"""


class DeployScriptTests(unittest.TestCase):
    def run_deploy(self, temp_dir: str) -> subprocess.CompletedProcess[str]:
        root = Path(temp_dir)
        env = os.environ.copy()
        env.update(
            {
            "TARGET_BIN": str(root / "bin" / "sshbox"),
            "TARGET_TEST": str(root / "bin" / "tests" / "test_sshbox.py"),
            "TARGET_CONFIG_DIR": str(root / ".config" / "sshbox"),
            "TARGET_CONFIG": str(root / ".config" / "sshbox" / "servers.json"),
            "TARGET_EXAMPLE": str(root / ".config" / "sshbox" / "servers.example.json"),
            }
        )
        return subprocess.run(
            [str(DEPLOY_SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def test_help_mentions_copy_and_link_modes(self):
        result = subprocess.run(
            [str(DEPLOY_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("copy", result.stdout)
        self.assertIn("link", result.stdout)

    def test_missing_servers_json_is_initialized_with_example_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_deploy(temp_dir)
            config_file = Path(temp_dir) / ".config" / "sshbox" / "servers.json"
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(config_file.exists())
            self.assertEqual(
                config_file.read_text(encoding="utf-8"),
                EXPECTED_SERVERS_TEMPLATE,
            )

    def test_existing_servers_json_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".config" / "sshbox"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "servers.json"
            custom_config = '[{"name":"custom","host":"1.2.3.4","user":"root","password":"secret"}]\n'
            config_file.write_text(custom_config, encoding="utf-8")

            result = self.run_deploy(temp_dir)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(config_file.read_text(encoding="utf-8"), custom_config)


if __name__ == "__main__":
    unittest.main()
