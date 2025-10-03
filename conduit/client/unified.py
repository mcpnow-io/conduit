import hashlib
import json
import time
from functools import wraps
from typing import Any, Dict, Optional

import httpx
from httpx import Limits, Timeout

from conduit.client.differential import DifferentialClient
from conduit.client.diffusion import DiffusionClient
from conduit.client.file import FileClient
from conduit.client.maniphest import ManiphestClient
from conduit.client.misc import (
    ConduitClient,
    FlagClient,
    HarbormasterClient,
    MacroClient,
    PasteClient,
    PhidClient,
    PhrictionClient,
    RemarkupClient,
)
from conduit.client.project import ProjectClient
from conduit.client.user import UserClient


class ClientConfig:
    """Enhanced client configuration with timeout and retry settings."""

    def __init__(
        self,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        read_timeout: float = 30.0,
        write_timeout: float = 30.0,
        pool_limits: Optional[Limits] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
        enable_cache: bool = True,
        cache_ttl: int = 300,  # 5 minutes
        **kwargs,
    ):
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.pool_limits = pool_limits or Limits(
            max_connections=100, max_keepalive_connections=20
        )
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self.extra_config = kwargs


class RequestCache:
    """Simple request cache with TTL support."""

    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache = {}

    @staticmethod
    def _canonicalize(value: Any) -> str:
        """Create a stable string representation suitable for cache keys."""
        if value is None:
            return ""
        if isinstance(value, (dict, list, tuple, set)):
            try:
                return json.dumps(value, sort_keys=True, default=str)
            except TypeError:
                return str(value)
        return str(value)

    def _generate_key(
        self,
        method: str,
        url: str,
        params: dict = None,
        data: dict = None,
        json_payload: Any = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Generate cache key from request parameters."""
        key_parts = [
            method.upper(),
            url,
            self._canonicalize(params),
            self._canonicalize(data),
            self._canonicalize(json_payload),
            self._canonicalize(extra),
        ]
        key_data = "|".join(key_parts)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get cached response if still valid."""
        if key in self._cache:
            cached_data, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return cached_data
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """Cache response with timestamp."""
        self._cache[key] = (value, time.time())

    def clear(self):
        """Clear all cached responses."""
        self._cache.clear()


# Global cache instance
_request_cache = RequestCache()


def retry_request(
    max_retries: int = 3, retry_delay: float = 1.0, retry_backoff: float = 2.0
):
    """
    Decorator for retrying HTTP requests with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (seconds)
        retry_backoff: Backoff multiplier for delay
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = retry_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (
                    httpx.TimeoutException,
                    httpx.NetworkError,
                    httpx.HTTPStatusError,
                ) as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= retry_backoff
                    else:
                        raise

            raise last_exception

        return wrapper

    return decorator


def cached_request(ttl: int = 300):
    """
    Decorator for caching HTTP requests.

    Args:
        ttl: Cache time-to-live in seconds
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0] if args else None

            # Resolve method and url from positional / keyword arguments.
            method = kwargs.get("method")
            url = kwargs.get("url")

            if len(args) >= 2:
                method = args[1] if method is None else method
            if len(args) >= 3:
                url = args[2] if url is None else url

            # If caching is disabled or we cannot determine the request
            # parameters, execute without caching.
            cache_enabled = True
            cache_ttl = ttl

            if instance is not None and hasattr(instance, "config"):
                config = getattr(instance, "config")
                cache_enabled = getattr(config, "enable_cache", True)
                cache_ttl = getattr(config, "cache_ttl", ttl)

            if not cache_enabled or method is None or url is None:
                return func(*args, **kwargs)

            method_upper = str(method).upper()
            # Only cache idempotent GET requests to avoid stale POST data.
            if method_upper != "GET":
                return func(*args, **kwargs)

            params = kwargs.get("params")
            data = kwargs.get("data")
            json_payload = kwargs.get("json")

            # Include remaining keyword arguments (e.g., headers) so that
            # different call signatures do not collide.
            extra_kwargs = {
                key: value
                for key, value in kwargs.items()
                if key not in {"method", "url", "params", "data", "json"}
            }

            cache_key = _request_cache._generate_key(
                method_upper,
                url,
                params=params,
                data=data,
                json_payload=json_payload,
                extra=extra_kwargs,
            )

            # Honour custom TTL per instance.
            _request_cache.ttl = cache_ttl

            cached_response = _request_cache.get(cache_key)
            if cached_response is not None:
                return cached_response

            result = func(*args, **kwargs)
            _request_cache.set(cache_key, result)
            return result

        return wrapper

    return decorator


class EnhancedPhabricatorClient(object):
    """Enhanced Phabricator client with improved HTTP configuration."""

    def __init__(
        self,
        api_url: str,
        api_token: str,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        read_timeout: float = 30.0,
        write_timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
        enable_cache: bool = True,
        cache_ttl: int = 300,
        **kwargs,
    ):
        # Initialize enhanced HTTP client
        self.http_client = httpx.Client(
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "ModelContextProtocol/1.0 (Enhanced; +https://github.com/modelcontextprotocol/servers)",
            },
            timeout=Timeout(
                connect=connect_timeout,
                read=read_timeout,
                write=write_timeout,
                timeout=timeout,
            ),
            limits=Limits(max_connections=100, max_keepalive_connections=20),
            follow_redirects=True,
            proxy=kwargs.get("proxy"),
            verify=not kwargs.get("disable_cert_verify", False),
        )

        # Store configuration
        self.config = ClientConfig(
            timeout=timeout,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            enable_cache=enable_cache,
            cache_ttl=cache_ttl,
            **kwargs,
        )

        # Initialize client modules
        self.maniphest = ManiphestClient(api_url, api_token, self.http_client)
        self.differential = DifferentialClient(api_url, api_token, self.http_client)
        self.diffusion = DiffusionClient(api_url, api_token, self.http_client)
        self.project = ProjectClient(api_url, api_token, self.http_client)
        self.user = UserClient(api_url, api_token, self.http_client)
        self.file = FileClient(api_url, api_token, self.http_client)
        self.conduit = ConduitClient(api_url, api_token, self.http_client)
        self.harbormaster = HarbormasterClient(api_url, api_token, self.http_client)
        self.paste = PasteClient(api_url, api_token, self.http_client)
        self.phriction = PhrictionClient(api_url, api_token, self.http_client)
        self.remarkup = RemarkupClient(api_url, api_token, self.http_client)
        self.macro = MacroClient(api_url, api_token, self.http_client)
        self.flag = FlagClient(api_url, api_token, self.http_client)
        self.phid = PhidClient(api_url, api_token, self.http_client)

    @retry_request(max_retries=3, retry_delay=1.0, retry_backoff=2.0)
    @cached_request(ttl=300)
    def request(self, method: str, url: str, **kwargs):
        """
        Make an HTTP request with retry and cache support.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            Response data
        """
        response = self.http_client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def clear_cache(self):
        """Clear all cached requests."""
        _request_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics and configuration."""
        return {
            "config": {
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "enable_cache": self.config.enable_cache,
                "cache_ttl": self.config.cache_ttl,
            },
            "cache_size": len(_request_cache._cache),
            "connection_pool": {
                "max_connections": (
                    self.http_client.limits.max_connections
                    if hasattr(self.http_client, "limits")
                    else "N/A"
                ),
                "max_keepalive_connections": (
                    self.http_client.limits.max_keepalive_connections
                    if hasattr(self.http_client, "limits")
                    else "N/A"
                ),
            },
        }

    def close(self):
        """Close the HTTP client."""
        if self.http_client:
            self.http_client.close()


class PhabricatorClient(object):
    """Backward-compatible Phabricator client with enhanced configuration."""

    def __init__(
        self,
        api_url: str,
        api_token: str,
        proxy: Optional[str] = None,
        disable_cert_verify: Optional[bool] = False,
        timeout: float = 30.0,
        max_retries: int = 3,
        enable_cache: bool = True,
        **kwargs,
    ):
        # Use enhanced client if advanced features are requested
        if (
            timeout != 30.0
            or max_retries != 3
            or (enable_cache and enable_cache is not True)
        ):
            self._enhanced_client = EnhancedPhabricatorClient(
                api_url=api_url,
                api_token=api_token,
                timeout=timeout,
                max_retries=max_retries,
                enable_cache=enable_cache,
                proxy=proxy,
                disable_cert_verify=disable_cert_verify,
                **kwargs,
            )
            self.http_client = self._enhanced_client.http_client
            self._is_enhanced = True
        else:
            # Use original simple client for backward compatibility
            self.http_client = httpx.Client(
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)",
                },
                timeout=30,
                follow_redirects=True,
                proxy=proxy,
                verify=not disable_cert_verify,
            )
            self._is_enhanced = False

        # Initialize client modules (same as before)
        self.maniphest = ManiphestClient(api_url, api_token, self.http_client)
        self.differential = DifferentialClient(api_url, api_token, self.http_client)
        self.diffusion = DiffusionClient(api_url, api_token, self.http_client)
        self.project = ProjectClient(api_url, api_token, self.http_client)
        self.user = UserClient(api_url, api_token, self.http_client)
        self.file = FileClient(api_url, api_token, self.http_client)
        self.conduit = ConduitClient(api_url, api_token, self.http_client)
        self.harbormaster = HarbormasterClient(api_url, api_token, self.http_client)
        self.paste = PasteClient(api_url, api_token, self.http_client)
        self.phriction = PhrictionClient(api_url, api_token, self.http_client)
        self.remarkup = RemarkupClient(api_url, api_token, self.http_client)
        self.macro = MacroClient(api_url, api_token, self.http_client)
        self.flag = FlagClient(api_url, api_token, self.http_client)
        self.phid = PhidClient(api_url, api_token, self.http_client)

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics if enhanced features are enabled."""
        if self._is_enhanced:
            return self._enhanced_client.get_stats()
        return {"message": "Basic client - no enhanced features enabled"}

    def clear_cache(self):
        """Clear cache if caching is enabled."""
        if hasattr(self, "_enhanced_client"):
            self._enhanced_client.clear_cache()

    def close(self):
        if self.http_client:
            self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
