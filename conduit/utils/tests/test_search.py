"""Tests for search utilities."""

from conduit.utils.search import (
    build_repository_search_constraints,
    build_search_constraints,
    build_task_search_constraints,
    build_user_search_constraints,
)


class TestBuildSearchConstraints:
    """Test general search constraints builder."""

    def test_build_search_constraints_empty(self):
        """Test building constraints with no inputs."""
        result = build_search_constraints()

        assert result == {}

    def test_build_search_constraints_with_base(self):
        """Test building constraints with base constraints."""
        base = {"status": "open"}
        result = build_search_constraints(base, priority="high")

        assert result == {"status": "open", "priority": "high"}

    def test_build_search_constraints_only_kwargs(self):
        """Test building constraints with only kwargs."""
        result = build_search_constraints(None, status="closed", limit=10)

        assert result == {"status": "closed", "limit": 10}

    def test_build_search_constraints_kwargs_override(self):
        """Test that kwargs override base constraints."""
        base = {"status": "open", "priority": "low"}
        result = build_search_constraints(base, priority="high")

        assert result == {"status": "open", "priority": "high"}


class TestBuildUserSearchConstraints:
    """Test user-specific search constraints builder."""

    def test_build_user_search_constraints_empty(self):
        """Test building user constraints with no inputs."""
        result = build_user_search_constraints()

        assert result == {}

    def test_build_user_search_constraints_with_ids(self):
        """Test building user constraints with IDs."""
        result = build_user_search_constraints(ids=[1, 2, 3])

        assert result == {"ids": [1, 2, 3]}

    def test_build_user_search_constraints_with_phids(self):
        """Test building user constraints with PHIDs."""
        phids = ["PHID-USER-1", "PHID-USER-2"]
        result = build_user_search_constraints(phids=phids)

        assert result == {"phids": phids}

    def test_build_user_search_constraints_with_usernames(self):
        """Test building user constraints with usernames."""
        usernames = ["alice", "bob"]
        result = build_user_search_constraints(usernames=usernames)

        assert result == {"usernames": usernames}

    def test_build_user_search_constraints_with_name_like(self):
        """Test building user constraints with name_like filter."""
        result = build_user_search_constraints(name_like="admin")

        assert result == {"nameLike": "admin"}

    def test_build_user_search_constraints_with_boolean_filters(self):
        """Test building user constraints with boolean filters."""
        result = build_user_search_constraints(
            is_admin=True,
            is_disabled=False,
            is_bot=None,
        )

        expected = {
            "isAdmin": True,
            "isDisabled": False,
        }
        assert result == expected

    def test_build_user_search_constraints_with_timestamps(self):
        """Test building user constraints with timestamps."""
        result = build_user_search_constraints(
            created_start=1609459200,  # 2021-01-01
            created_end=1640995200,  # 2022-01-01
        )

        expected = {
            "createdStart": 1609459200,
            "createdEnd": 1640995200,
        }
        assert result == expected

    def test_build_user_search_constraints_with_fulltext(self):
        """Test building user constraints with fulltext query."""
        result = build_user_search_constraints(fulltext_query="john doe")

        assert result == {"query": "john doe"}

    def test_build_user_search_constraints_with_additional_kwargs(self):
        """Test building user constraints with additional kwargs."""
        result = build_user_search_constraints(
            ids=[1],
            custom_field="custom_value",
        )

        expected = {
            "ids": [1],
            "custom_field": "custom_value",
        }
        assert result == expected

    def test_build_user_search_constraints_comprehensive(self):
        """Test building user constraints with all parameters."""
        result = build_user_search_constraints(
            ids=[1, 2],
            phids=["PHID-USER-1"],
            usernames=["admin"],
            name_like="test",
            is_admin=True,
            is_disabled=False,
            is_bot=False,
            is_mailing_list=False,
            needs_approval=None,
            mfa=True,
            created_start=1609459200,
            created_end=1640995200,
            fulltext_query="search term",
            custom_param="custom",
        )

        expected = {
            "ids": [1, 2],
            "phids": ["PHID-USER-1"],
            "usernames": ["admin"],
            "nameLike": "test",
            "isAdmin": True,
            "isDisabled": False,
            "isBot": False,
            "isMailingList": False,
            "mfa": True,
            "createdStart": 1609459200,
            "createdEnd": 1640995200,
            "query": "search term",
            "custom_param": "custom",
        }
        assert result == expected


class TestBuildTaskSearchConstraints:
    """Test task-specific search constraints builder."""

    def test_build_task_search_constraints_empty(self):
        """Test building task constraints with no inputs."""
        result = build_task_search_constraints()

        assert result == {}

    def test_build_task_search_constraints_with_assigned(self):
        """Test building task constraints with assignees."""
        result = build_task_search_constraints(assigned=["alice", "PHID-USER-1"])

        assert result == {"assigned": ["alice", "PHID-USER-1"]}

    def test_build_task_search_constraints_with_author_phids(self):
        """Test building task constraints with author PHIDs."""
        phids = ["PHID-USER-1", "PHID-USER-2"]
        result = build_task_search_constraints(author_phids=phids)

        assert result == {"authorPHIDs": phids}

    def test_build_task_search_constraints_with_statuses(self):
        """Test building task constraints with statuses."""
        statuses = ["open", "closed"]
        result = build_task_search_constraints(statuses=statuses)

        assert result == {"statuses": statuses}

    def test_build_task_search_constraints_with_priorities(self):
        """Test building task constraints with priorities."""
        priorities = [90, 100]
        result = build_task_search_constraints(priorities=priorities)

        assert result == {"priorities": priorities}

    def test_build_task_search_constraints_with_projects(self):
        """Test building task constraints with projects."""
        projects = ["project1", "PHID-PROJ-1"]
        result = build_task_search_constraints(projects=projects)

        assert result == {"projects": projects}

    def test_build_task_search_constraints_with_relationships(self):
        """Test building task constraints with relationship filters."""
        result = build_task_search_constraints(
            has_parents=True,
            has_subtasks=False,
        )

        expected = {
            "hasParents": True,
            "hasSubtasks": False,
        }
        assert result == expected

    def test_build_task_search_constraints_with_timestamps(self):
        """Test building task constraints with timestamps."""
        result = build_task_search_constraints(
            created_after=1609459200,
            created_before=1640995200,
            modified_after=1612137600,
            modified_before=1642579200,
        )

        expected = {
            "createdStart": 1609459200,
            "createdEnd": 1640995200,
            "modifiedStart": 1612137600,
            "modifiedEnd": 1642579200,
        }
        assert result == expected

    def test_build_task_search_constraints_comprehensive(self):
        """Test building task constraints with all parameters."""
        result = build_task_search_constraints(
            assigned=["alice"],
            author_phids=["PHID-USER-1"],
            statuses=["open"],
            priorities=[90],
            projects=["project1"],
            subscribers=["bob"],
            fulltext_query="bug fix",
            has_parents=True,
            has_subtasks=False,
            created_after=1609459200,
            created_before=1640995200,
            modified_after=1612137600,
            modified_before=1642579200,
            custom_field="custom",
        )

        expected = {
            "assigned": ["alice"],
            "authorPHIDs": ["PHID-USER-1"],
            "statuses": ["open"],
            "priorities": [90],
            "projects": ["project1"],
            "subscribers": ["bob"],
            "query": "bug fix",
            "hasParents": True,
            "hasSubtasks": False,
            "createdStart": 1609459200,
            "createdEnd": 1640995200,
            "modifiedStart": 1612137600,
            "modifiedEnd": 1642579200,
            "custom_field": "custom",
        }
        assert result == expected


class TestBuildRepositorySearchConstraints:
    """Test repository-specific search constraints builder."""

    def test_build_repository_search_constraints_empty(self):
        """Test building repository constraints with no inputs."""
        result = build_repository_search_constraints()

        assert result == {}

    def test_build_repository_search_constraints_with_name_contains(self):
        """Test building repository constraints with name filter."""
        result = build_repository_search_constraints(name_contains="test")

        assert result == {"name": "test"}

    def test_build_repository_search_constraints_with_vcs_type(self):
        """Test building repository constraints with VCS type."""
        result = build_repository_search_constraints(vcs_type="git")

        assert result == {"vcs": "git"}

    def test_build_repository_search_constraints_with_status(self):
        """Test building repository constraints with status."""
        result = build_repository_search_constraints(status="active")

        assert result == {"status": "active"}

    def test_build_repository_search_constraints_with_callsigns(self):
        """Test building repository constraints with callsigns."""
        callsigns = ["TEST", "DEMO"]
        result = build_repository_search_constraints(callsigns=callsigns)

        assert result == {"callsigns": callsigns}

    def test_build_repository_search_constraints_with_names(self):
        """Test building repository constraints with names."""
        names = ["test-repo", "demo-repo"]
        result = build_repository_search_constraints(names=names)

        assert result == {"names": names}

    def test_build_repository_search_constraints_with_short_names(self):
        """Test building repository constraints with short names."""
        short_names = ["test", "demo"]
        result = build_repository_search_constraints(short_names=short_names)

        assert result == {"shortNames": short_names}

    def test_build_repository_search_constraints_comprehensive(self):
        """Test building repository constraints with all parameters."""
        result = build_repository_search_constraints(
            name_contains="example",
            vcs_type="git",
            status="active",
            callsigns=["EX"],
            names=["example-repo"],
            short_names=["ex"],
            custom_field="custom",
        )

        expected = {
            "name": "example",
            "vcs": "git",
            "status": "active",
            "callsigns": ["EX"],
            "names": ["example-repo"],
            "shortNames": ["ex"],
            "custom_field": "custom",
        }
        assert result == expected
