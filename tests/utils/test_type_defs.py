"""Tests for type definitions and validation utilities."""

from pathlib import Path

import pytest

from hashreport.utils.type_defs import (
    FilePath,
    FileProcessor,
    Hashable,
    HashAlgorithm,
    ReportData,
    ReportEntry,
    ReportFormat,
    ReportHandler,
    ensure_dict,
    ensure_list,
    is_valid_report_entry,
    safe_cast,
    validate_email_address,
    validate_file_path,
    validate_hash_algorithm,
    validate_hostname,
    validate_port_number,
    validate_report_data,
    validate_report_format,
)


class TestTypeAliases:
    """Test type alias definitions."""

    def test_file_path_types(self):
        """Test FilePath type accepts string and Path."""
        # These should not raise type errors
        str_path: FilePath = "test.txt"
        path_obj: FilePath = Path("test.txt")

        assert isinstance(str_path, (str, Path))
        assert isinstance(path_obj, Path)

    def test_hash_algorithm_types(self):
        """Test HashAlgorithm type accepts valid algorithms."""
        valid_algorithms: list[HashAlgorithm] = [
            "md5",
            "sha1",
            "sha256",
            "sha512",
            "blake2b",
        ]
        for algo in valid_algorithms:
            assert isinstance(algo, str)

    def test_report_format_types(self):
        """Test ReportFormat type accepts valid formats."""
        valid_formats: list[ReportFormat] = ["csv", "json"]
        for fmt in valid_formats:
            assert isinstance(fmt, str)

    def test_report_entry_structure(self):
        """Test ReportEntry type structure."""
        entry: ReportEntry = {
            "file": "test.txt",
            "hash": "abc123",
            "size": 1024,
            "modified": "2023-01-01",
            "algorithm": "md5",
        }
        assert isinstance(entry, dict)

    def test_report_data_structure(self):
        """Test ReportData type structure."""
        data: ReportData = [
            {"file": "test1.txt", "hash": "abc123"},
            {"file": "test2.txt", "hash": "def456"},
        ]
        assert isinstance(data, list)
        assert all(isinstance(entry, dict) for entry in data)


class TestProtocols:
    """Test protocol definitions."""

    def test_hashable_protocol(self):
        """Test Hashable protocol."""

        class HashableObject:
            def __hash__(self) -> int:
                return hash("test")

        obj = HashableObject()
        assert isinstance(obj, Hashable)

    def test_file_processor_protocol(self):
        """Test FileProcessor protocol."""

        def process_file(filepath: FilePath) -> str:
            return str(filepath)

        assert isinstance(process_file, FileProcessor)

    def test_report_handler_protocol(self):
        """Test ReportHandler protocol."""

        class MockHandler:
            def read(self) -> ReportData:
                return []

            def write(self, data: ReportData, **kwargs) -> None:
                pass

            def append(self, entry: ReportEntry) -> None:
                pass

        handler = MockHandler()
        assert isinstance(handler, ReportHandler)


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_file_path_valid(self):
        """Test validate_file_path with valid paths."""
        valid_paths = ["/path/to/file", Path("/path/to/file"), "relative/path"]
        for path in valid_paths:
            result = validate_file_path(path)
            assert result == path

    def test_validate_file_path_invalid(self):
        """Test validate_file_path with invalid paths."""
        invalid_paths = [123, None, [], {}, ("tuple", "not", "path")]
        for path in invalid_paths:
            with pytest.raises(ValueError, match="Invalid file path type"):
                validate_file_path(path)

    def test_validate_hash_algorithm_valid(self):
        """Test validate_hash_algorithm with valid algorithms."""
        valid_algorithms = ["md5", "sha1", "sha256", "sha512", "blake2b"]
        for algo in valid_algorithms:
            result = validate_hash_algorithm(algo)
            assert result == algo.lower()

            # Test case insensitivity
            result = validate_hash_algorithm(algo.upper())
            assert result == algo.lower()

    def test_validate_hash_algorithm_invalid(self):
        """Test validate_hash_algorithm with invalid algorithms."""
        invalid_algorithms = ["invalid", "sha3", "ripemd160", ""]
        for algo in invalid_algorithms:
            with pytest.raises(ValueError, match="Unsupported hash algorithm"):
                validate_hash_algorithm(algo)

    def test_validate_hash_algorithm_case_insensitive(self):
        """Test validate_hash_algorithm with different cases."""
        algorithms = ["MD5", "Sha1", "SHA256", "sha512", "BLAKE2B"]
        for algorithm in algorithms:
            result = validate_hash_algorithm(algorithm)
            assert result == algorithm.lower()

    def test_validate_report_format_valid(self):
        """Test validate_report_format with valid formats."""
        valid_formats = ["csv", "json"]
        for fmt in valid_formats:
            result = validate_report_format(fmt)
            assert result == fmt.lower()

            # Test case insensitivity
            result = validate_report_format(fmt.upper())
            assert result == fmt.lower()

    def test_validate_report_format_invalid(self):
        """Test validate_report_format with invalid formats."""
        invalid_formats = ["xml", "yaml", "txt", ""]
        for fmt in invalid_formats:
            with pytest.raises(ValueError, match="Unsupported report format"):
                validate_report_format(fmt)

    def test_validate_report_format_case_insensitive(self):
        """Test validate_report_format with different cases."""
        formats = ["CSV", "Json", "JSON"]
        for format_str in formats:
            result = validate_report_format(format_str)
            assert result == format_str.lower()

    def test_validate_email_address_valid(self):
        """Test validate_email_address with valid emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com",
        ]
        for email in valid_emails:
            result = validate_email_address(email)
            # NewType can't be used with isinstance, but we can check the value
            assert result == email
            assert isinstance(result, str)

    def test_validate_email_address_invalid(self):
        """Test validate_email_address with invalid emails."""
        invalid_emails = [
            "invalid-email",  # No @ symbol
            "@example.com",  # No local part
            "user@",  # No domain
            "user@.com",  # Domain starts with dot
            "",  # Empty string
            "user@domain",  # Missing TLD
            "user@example",  # Missing TLD
            "user@@example.com",  # Double @
        ]
        for email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email address format"):
                validate_email_address(email)

    def test_validate_port_number_valid(self):
        """Test validate_port_number with valid ports."""
        valid_ports = [1, 80, 443, 8080, 65535]
        for port in valid_ports:
            result = validate_port_number(port)
            # NewType can't be used with isinstance, but we can check the value
            assert result == port
            assert isinstance(result, int)

    def test_validate_port_number_invalid(self):
        """Test validate_port_number with invalid ports."""
        invalid_ports = [0, -1, 65536, 99999]
        for port in invalid_ports:
            with pytest.raises(ValueError, match="Invalid port number"):
                validate_port_number(port)

    def test_validate_hostname_valid(self):
        """Test validate_hostname with valid hostnames."""
        valid_hostnames = [
            "example.com",
            "subdomain.example.org",
            "test.co.uk",
            "localhost.localdomain",
        ]
        for hostname in valid_hostnames:
            result = validate_hostname(hostname)
            # NewType can't be used with isinstance, but we can check the value
            assert result == hostname
            assert isinstance(result, str)

    def test_validate_hostname_invalid(self):
        """Test validate_hostname with invalid hostnames."""
        invalid_hostnames = [
            "invalid",  # No dot
            ".example.com",  # Starts with dot
            "example.",  # Ends with dot
            "",
            "example",  # No TLD
        ]
        for hostname in invalid_hostnames:
            with pytest.raises(ValueError, match="Invalid hostname format"):
                validate_hostname(hostname)


class TestReportDataValidation:
    """Test report data validation functions."""

    def test_is_valid_report_entry_valid(self):
        """Test is_valid_report_entry with valid entries."""
        valid_entries = [
            {"file": "test.txt", "hash": "abc123"},
            {"File Path": "test.txt", "Hash Value": "abc123"},
            {"any": "dict", "is": "valid"},
            {},
        ]
        for entry in valid_entries:
            assert is_valid_report_entry(entry)

    def test_is_valid_report_entry_invalid(self):
        """Test is_valid_report_entry with invalid entries."""
        invalid_entries = ["not a dict", 123, None, [], ("tuple", "not", "dict")]
        for entry in invalid_entries:
            assert not is_valid_report_entry(entry)

    def test_validate_report_data_valid(self):
        """Test validate_report_data with valid data."""
        valid_data = [
            [{"file": "test1.txt", "hash": "abc123"}],
            [{"file": "test1.txt"}, {"file": "test2.txt"}],
            [],
        ]
        for data in valid_data:
            result = validate_report_data(data)
            assert result == data

    def test_validate_report_data_invalid(self):
        """Test validate_report_data with invalid data."""
        # Not a list
        with pytest.raises(ValueError, match="Report data must be a list"):
            validate_report_data("not a list")

        with pytest.raises(ValueError, match="Report data must be a list"):
            validate_report_data({"not": "a list"})

        # List with invalid entries
        invalid_data = [
            [{"file": "test.txt"}, "not a dict"],
            [123, {"file": "test.txt"}],
            [None, {"file": "test.txt"}],
        ]
        for data in invalid_data:
            with pytest.raises(ValueError, match="Invalid report entry at index"):
                validate_report_data(data)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_safe_cast_success(self):
        """Test safe_cast with successful conversions."""
        # String to int
        result = safe_cast("123", int)
        assert result == 123

        # String to float
        result = safe_cast("123.45", float)
        assert result == 123.45

        # Already correct type
        result = safe_cast(123, int)
        assert result == 123

    def test_safe_cast_failure_with_default(self):
        """Test safe_cast with failed conversions and default."""
        # Invalid conversion with default
        result = safe_cast("not a number", int, default=0)
        assert result == 0

        # Invalid conversion without default
        result = safe_cast("not a number", int)
        assert result is None

    def test_safe_cast_failure_types(self):
        """Test safe_cast with various failure types."""
        # TypeError
        result = safe_cast(None, int)
        assert result is None

        # ValueError
        result = safe_cast("abc", int)
        assert result is None

    def test_safe_cast_with_complex_types(self):
        """Test safe_cast with more complex type conversions."""
        # List to tuple
        result = safe_cast([1, 2, 3], tuple)
        assert result == (1, 2, 3)

        # String to list (if supported)
        result = safe_cast("abc", list)
        assert result == ["a", "b", "c"]

    def test_safe_cast_with_none_and_default(self):
        """Test safe_cast with None and default values."""
        # None with default
        result = safe_cast(None, int, default=42)
        assert result == 42

        # None without default
        result = safe_cast(None, str)
        assert result == "None"

    def test_safe_cast_with_custom_objects(self):
        """Test safe_cast with custom objects."""

        class CustomInt:
            def __init__(self, value):
                self.value = value

            def __int__(self):
                return self.value

        obj = CustomInt(123)
        result = safe_cast(obj, int)
        assert result == 123

    def test_ensure_list_single_item(self):
        """Test ensure_list with single item."""
        result = ensure_list("test")
        assert result == ["test"]

        result = ensure_list(123)
        assert result == [123]

    def test_ensure_list_already_list(self):
        """Test ensure_list with already list."""
        test_list = ["item1", "item2"]
        result = ensure_list(test_list)
        assert result == test_list
        assert result is test_list  # Same object

    def test_ensure_dict_dict(self):
        """Test ensure_dict with dictionary."""
        test_dict = {"key": "value"}
        result = ensure_dict(test_dict)
        assert result == test_dict
        assert result is test_dict  # Same object

    def test_ensure_dict_object_with_dict(self):
        """Test ensure_dict with object that has __dict__."""

        class TestObject:
            def __init__(self):
                self.attr1 = "value1"
                self.attr2 = "value2"

        obj = TestObject()
        result = ensure_dict(obj)
        assert result == {"attr1": "value1", "attr2": "value2"}

    def test_ensure_dict_invalid(self):
        """Test ensure_dict with invalid types."""
        invalid_values = ["string", 123, None, []]
        for value in invalid_values:
            with pytest.raises(ValueError, match="Cannot convert"):
                ensure_dict(value)

    def test_ensure_dict_with_namedtuple(self):
        """Test ensure_dict with namedtuple."""
        from collections import namedtuple

        TestTuple = namedtuple("TestTuple", ["a", "b"])
        obj = TestTuple(1, 2)
        with pytest.raises(ValueError, match="Cannot convert"):
            ensure_dict(obj)

    def test_ensure_dict_with_slots(self):
        """Test ensure_dict with object using __slots__."""

        class SlottedObject:
            __slots__ = ["attr1", "attr2"]

            def __init__(self):
                self.attr1 = "value1"
                self.attr2 = "value2"

        obj = SlottedObject()
        with pytest.raises(ValueError, match="Cannot convert"):
            ensure_dict(obj)
