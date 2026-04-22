import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/theoryxu/IdeaProjects/sshbox")
DEPLOY_SCRIPT = REPO_ROOT / "deploy.sh"


class DeployScriptTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
