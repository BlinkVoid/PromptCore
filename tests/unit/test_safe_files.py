import pytest
from pathlib import Path
from promptsmith.utils.safe_files import SafeFileManager

class TestSafeFileManager:
    def test_sanitize_filename_removes_path_traversal(self):
        unsafe = "../../../etc/passwd"
        safe = SafeFileManager.sanitize_filename(unsafe)
        assert ".." not in safe
        assert "/" not in safe
        # Implementation replaces dots/slashes with underscores to neutralize path traversal
        assert safe == "_._._etc_passwd"
        
    def test_sanitize_filename_simple(self):
        assert SafeFileManager.sanitize_filename("valid_file.txt") == "valid_file.txt"

    def test_sanitize_filename_complex(self):
        unsafe = "file/with\\bad:chars.txt"
        safe = SafeFileManager.sanitize_filename(unsafe)
        assert "/" not in safe
        assert "\\" not in safe
        assert ":" not in safe

    def test_get_safe_path_valid(self, tmp_path):
        base = tmp_path
        path = SafeFileManager.get_safe_path(base, "data.json")
        assert path == base / "data.json"

    def test_get_safe_path_traversal(self, tmp_path):
        base = tmp_path
        # Even if sanitize failed (which it shouldn't), get_safe_path checks the resolved path
        # But since sanitize runs first, we can't easily force a traversal unless we bypass sanitize
        # This test ensures that a "traversal-like" filename is neutralized
        path = SafeFileManager.get_safe_path(base, "../data.json")
        # Implementation converts ".." to "_." or similar depending on regex match, 
        # and slashes to underscores. Here "../data.json" -> "_data.json" because of lstrip('./\\')?
        # No. ".." -> "." via first regex. 
        # Wait, implementation says: re.sub(r'\.{2,}', '.', filename) -> ".." becomes "."
        # So "../data.json" -> "./data.json"
        # Then re.sub(r'[^\w\.\-]', '_', name) -> "./data.json" (slash becomes underscore? No slash is not in \w.-)
        # So it becomes "._data.json"
        # Then lstrip('./\\') -> "_data.json"
        assert path == base / "_data.json"
        assert str(path).startswith(str(base))
