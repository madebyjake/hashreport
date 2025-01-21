"""Temporary test file to verify GitHub Workflow functionality."""


def add_numbers(a, b):
    """Add two numbers together and return the result.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        int: Sum of a and b
    """
    return a + b


def test_add_numbers():
    """Basic test to verify pytest is working."""
    result = add_numbers(2, 3)
    assert result == 5
