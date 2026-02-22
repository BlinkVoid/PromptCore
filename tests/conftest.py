import pytest
from unittest.mock import MagicMock
from pathlib import Path

# Fix for "RuntimeError: Event loop is closed" on Windows
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from promptsmith.main import Dependencies, get_dependencies, mcp
from promptsmith.persistence import Storage

@pytest.fixture
def mock_deps():
    """Create a mock dependency container."""
    deps = MagicMock(spec=Dependencies)
    deps.selector = MagicMock()
    deps.builder = MagicMock()
    deps.storage = MagicMock()
    return deps

@pytest.fixture
def override_deps(mock_deps):
    """Override the global dependency container for tests."""
    from promptsmith import main
    original_deps = main._deps
    main._deps = mock_deps
    yield mock_deps
    main._deps = original_deps

@pytest.fixture
def in_memory_storage():
    """Create a real Storage instance using in-memory SQLite."""
    storage = Storage(db_url="sqlite:///:memory:")
    storage.initialize()
    return storage
