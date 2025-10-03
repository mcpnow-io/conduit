from conduit.client.types import validate_search_constraints
from conduit.client.unified import ClientConfig, cached_request
from conduit.client.unified import _request_cache as global_request_cache
from conduit.tools.handlers import _get_error_details
from conduit.utils.validation import RuntimeValidationClient


class DummyUserAPI:
    def query(self, phids):
        # Mirrors actual conduit payload: plain result dict keyed by PHID
        return {phids[0]: {"phid": phids[0]}}


class DummyBaseClient:
    def __init__(self):
        self.user = DummyUserAPI()


def test_runtime_validation_accepts_plain_conduit_payload():
    client = RuntimeValidationClient(DummyBaseClient())

    result = client.get_user_info("PHID-USER-123")
    assert "PHID-USER-123" in result


def test_task_constraints_allow_has_parents():
    # Maniphest supports this filter; validator should accept it
    assert validate_search_constraints({"hasParents": True}, "task")


def test_cached_request_keys_include_method():
    class DummyClient:
        def __init__(self):
            self.calls = 0
            self.config = ClientConfig(enable_cache=True)

        @cached_request(ttl=1)
        def request(self, method, url, **kwargs):
            self.calls += 1
            return {"call": self.calls}

    client = DummyClient()
    global_request_cache.clear()

    first = client.request("GET", "https://example.com")
    second = client.request("GET", "https://example.com")
    assert first == second
    assert client.calls == 1

    post_result = client.request("POST", "https://example.com")
    assert post_result["call"] == 2


def test_error_handler_handles_unknown_error_codes():
    class DummyError(Exception):
        pass

    class FakeAPIError(DummyError):
        def __init__(self, code):
            self.error_code = code

    details = _get_error_details(FakeAPIError("ERR-CONDUIT-CORE"))
    assert details["error_code"] == "UNKNOWN_ERROR"
