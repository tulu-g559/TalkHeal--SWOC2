"""
Pytest-based OAuth Test Suite
Run with: pytest -v
"""

import pytest
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# -----------------------------
# OAuth Config Tests
# -----------------------------

def test_oauth_config():
    """Ensure at least one OAuth provider is configured properly"""
    from auth.oauth_config import oauth_config

    providers = oauth_config.get_available_providers()
    assert isinstance(providers, list)

    assert len(providers) > 0, (
        "No OAuth providers configured. "
        "Ensure credentials are set in .env"
    )

    for provider in providers:
        config = oauth_config.get_provider(provider)

        assert config.client_id is not None
        assert config.client_secret is not None
        assert config.redirect_uri is not None

        # Validate redirect URI structure
        parsed = urlparse(config.redirect_uri)
        assert parsed.scheme in ["http", "https"]
        assert parsed.netloc != ""


# -----------------------------
# Database Tests
# -----------------------------

def test_database_initialization():
    """Ensure database initializes without error"""
    from auth.auth_utils import init_db

    # Should not raise any exception
    init_db()


# -----------------------------
# OAuth Utility Tests
# -----------------------------

def test_state_generation_entropy():
    """Ensure generated states are unique and sufficiently long"""
    from auth.oauth_utils import generate_state

    states = {generate_state() for _ in range(300)}

    # Ensure uniqueness
    assert len(states) == 300

    # Ensure reasonable entropy length
    for state in states:
        assert len(state) >= 32


def test_state_storage_and_verification():
    """Ensure stored state verifies correctly"""
    from auth.oauth_utils import generate_state, store_oauth_state, verify_oauth_state

    state = generate_state()
    store_oauth_state(state, "google")

    provider = verify_oauth_state(state)
    assert provider == "google"


def test_state_reuse_protection():
    """Ensure state cannot be reused (prevents replay attacks)"""
    from auth.oauth_utils import generate_state, store_oauth_state, verify_oauth_state

    state = generate_state()
    store_oauth_state(state, "google")

    # First verification should pass
    assert verify_oauth_state(state) == "google"

    # Second verification should fail
    assert verify_oauth_state(state) is None


def test_invalid_state_rejected():
    """Ensure invalid state is rejected"""
    from auth.oauth_utils import verify_oauth_state

    assert verify_oauth_state("invalid-state") is None
