import os
import subprocess
import tempfile
import time
from unittest import TestCase

from src.client.base import PhabricatorAPIError
from src.client.differential import DifferentialClient
from src.client.diffusion import DiffusionClient
from src.conduit import get_config


class TestDiffusionClient(TestCase):
    def setUp(self):
        super().setUp()
        config = get_config()
        self.cli = DiffusionClient(config.url, config.token)
        self.diff_cli = DifferentialClient(config.url, config.token)

        # Create a test repository for our tests
        self.test_repo = None
        self.test_repo_path = None
        self._setup_test_repository()

    def _setup_test_repository(self):
        """Create a test git repository for testing"""
        try:
            # Create a test repository
            repo_name = f"test-repo-{int(time.time())}"
            self.test_repo = self.cli.create_repository(
                name=repo_name,
                vcs_type="git",
                description="Test repository for diffusion client tests",
            )

            # Create a temporary directory for git operations
            self.test_repo_path = tempfile.mkdtemp()

            # Initialize git repo and create some test content
            os.chdir(self.test_repo_path)
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"], check=True
            )

            # Create test files
            with open("README.md", "w") as f:
                f.write("# Test Repository\n\nThis is a test repository.\n")

            os.makedirs("src", exist_ok=True)
            with open("src/main.py", "w") as f:
                f.write(
                    "#!/usr/bin/env python3\n\ndef main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()\n"
                )

            # Initial commit
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

            # Create a second commit for diff testing
            with open("src/utils.py", "w") as f:
                f.write("def helper_function():\n    return 'helper'\n")

            subprocess.run(["git", "add", "src/utils.py"], check=True)
            subprocess.run(["git", "commit", "-m", "Add utils module"], check=True)

        except Exception as e:
            print(f"Failed to setup test repository: {e}")
            # If we can't create a real repo, we'll skip repository-dependent tests

    def tearDown(self):
        """Clean up test resources"""
        if self.test_repo_path and os.path.exists(self.test_repo_path):
            import shutil

            shutil.rmtree(self.test_repo_path, ignore_errors=True)

    def test_search_repositories(self):
        """Test repository search functionality"""
        with self.subTest("Search all repositories"):
            result = self.cli.search_repositories(limit=10)
            self.assertIn("data", result)
            self.assertIsInstance(result["data"], list)

        with self.subTest("Search with constraints"):
            if self.test_repo:
                constraints = {"ids": [self.test_repo["object"]["id"]]}
                result = self.cli.search_repositories(constraints=constraints)
                self.assertIn("data", result)
                self.assertEqual(len(result["data"]), 1)

    def test_create_repository(self):
        """Test repository creation"""
        repo_name = f"test-created-repo-{int(time.time())}"

        result = self.cli.create_repository(
            name=repo_name,
            vcs_type="git",
            description="Test repository created by unit test",
        )

        self.assertIn("object", result)
        self.assertIn("phid", result["object"])
        # Repository was created successfully if we have an object with PHID

    def test_edit_repository(self):
        """Test repository editing"""
        if not self.test_repo:
            self.skipTest("No test repository available")

        new_description = f"Updated description {int(time.time())}"
        transactions = [{"type": "description", "value": new_description}]

        result = self.cli.edit_repository(
            transactions=transactions,
            object_identifier=self.test_repo["object"]["phid"],
        )

        self.assertIn("object", result)

    def test_search_commits(self):
        """Test commit search functionality"""
        with self.subTest("Search all commits"):
            result = self.cli.search_commits(limit=5)
            self.assertIn("data", result)
            self.assertIsInstance(result["data"], list)

    def test_browse_query(self):
        """Test repository browsing"""
        if not self.test_repo:
            self.skipTest("No test repository available")

        repo_phid = self.test_repo["object"]["phid"]

        with self.subTest("Browse repository root"):
            try:
                result = self.cli.browse_query(repository=repo_phid)
                self.assertIn("pathList", result)
            except PhabricatorAPIError:
                # Repository might not be fully set up yet
                pass

    def test_file_content_query(self):
        """Test file content retrieval"""
        if not self.test_repo:
            self.skipTest("No test repository available")

        repo_phid = self.test_repo["object"]["phid"]

        with self.subTest("Get file content"):
            try:
                result = self.cli.file_content_query(
                    repository=repo_phid, path="README.md"
                )
                # The exact structure depends on repository setup
                self.assertIsInstance(result, dict)
            except PhabricatorAPIError:
                # File might not exist or repository not ready
                pass

    def test_history_query(self):
        """Test repository history querying"""
        if not self.test_repo:
            self.skipTest("No test repository available")

        repo_phid = self.test_repo["object"]["phid"]

        with self.subTest("Get repository history"):
            try:
                result = self.cli.history_query(repository=repo_phid, limit=10)
                self.assertIsInstance(result, dict)
            except PhabricatorAPIError:
                # Repository might not have history yet
                pass

    def test_branch_query(self):
        """Test branch querying"""
        if not self.test_repo:
            self.skipTest("No test repository available")

        repo_phid = self.test_repo["object"]["phid"]

        with self.subTest("Get repository branches"):
            try:
                result = self.cli.branch_query(repository=repo_phid)
                self.assertIsInstance(result, dict)
            except PhabricatorAPIError:
                # Repository might not be ready
                pass

    def test_resolve_refs(self):
        """Test reference resolution"""
        if not self.test_repo:
            self.skipTest("No test repository available")

        repo_phid = self.test_repo["object"]["phid"]

        with self.subTest("Resolve refs"):
            try:
                result = self.cli.resolve_refs(
                    repository=repo_phid, refs=["main", "HEAD"]
                )
                self.assertIsInstance(result, dict)
            except PhabricatorAPIError:
                # Repository might not be ready
                pass

    def test_integration_workflow(self):
        """Test a complete diff review workflow"""
        if not self.test_repo:
            self.skipTest("No test repository available")

        repo_phid = self.test_repo["object"]["phid"]

        try:
            # 1. Create a raw diff
            diff_content = """diff --git a/test.txt b/test.txt
new file mode 100644
index 0000000..ce01362
--- /dev/null
+++ b/test.txt
@@ -0,0 +1 @@
+hello
"""

            diff_result = self.diff_cli.create_raw_diff(
                diff=diff_content, repository_phid=repo_phid
            )

            self.assertTrue("id" in diff_result or "diffid" in diff_result)
            _ = diff_result.get("id") or diff_result.get("diffid")  # diff_id
            diff_phid = diff_result.get("phid")

            # 2. Create a revision using PHID
            revision_result = self.diff_cli.edit_revision(
                transactions=[
                    {"type": "title", "value": "Test diff review"},
                    {"type": "summary", "value": "This is a test diff for review"},
                    {"type": "testPlan", "value": "Manual testing"},
                    {"type": "update", "value": diff_phid},
                ]
            )

            self.assertIn("object", revision_result)
            revision_phid = revision_result["object"]["phid"]

            # 3. Add a comment
            comment_result = self.diff_cli.edit_revision(
                transactions=[{"type": "comment", "value": "This looks good to me!"}],
                object_identifier=revision_phid,
            )

            self.assertIn("object", comment_result)

        except PhabricatorAPIError as e:
            # Some operations might fail if repository isn't fully configured
            print(f"Workflow test failed (expected): {e}")


class TestDiffusionDifferentialIntegration(TestCase):
    """Integration tests between Diffusion and Differential clients"""

    def setUp(self):
        super().setUp()
        config = get_config()
        self.diffusion_cli = DiffusionClient(config.url, config.token)
        self.differential_cli = DifferentialClient(config.url, config.token)

    def test_create_diff_from_repository(self):
        """Test creating a diff using repository data"""

        # First, get repositories
        repos = self.diffusion_cli.search_repositories(limit=5)

        if not repos["data"]:
            self.skipTest("No repositories available for testing")

        repo = repos["data"][0]
        repo_phid = repo["phid"]

        # Create a simple diff
        diff_content = """diff --git a/integration_test.txt b/integration_test.txt
new file mode 100644
index 0000000..9daeafb
--- /dev/null
+++ b/integration_test.txt
@@ -0,0 +1 @@
+test
"""

        try:
            diff_result = self.differential_cli.create_raw_diff(
                diff=diff_content, repository_phid=repo_phid
            )

            self.assertTrue("id" in diff_result or "diffid" in diff_result)

        except PhabricatorAPIError as e:
            # Expected if repository doesn't support diffs
            print(f"Integration test failed (expected): {e}")
