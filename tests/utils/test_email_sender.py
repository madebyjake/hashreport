"""Tests for the email sender utility."""

from email.mime.multipart import MIMEMultipart
from unittest.mock import MagicMock, patch

import pytest

from hashreport.utils.email_sender import EmailSender


@pytest.fixture
def email_sender():
    """Create an EmailSender instance for testing."""
    return EmailSender(
        host="test.smtp.com",
        port=587,
        username="test@example.com",
        password="password123",
    )


@pytest.fixture
def mock_smtp():
    """Create a mock SMTP server."""
    with patch("smtplib.SMTP") as mock:
        mock_server = MagicMock()
        mock.return_value.__enter__.return_value = mock_server
        yield mock_server


def test_init_with_params():
    """Test initialization with explicit parameters."""
    sender = EmailSender(
        host="smtp.test.com",
        port=25,
        username="user",
        password="pass",
        use_tls=False,
    )

    assert sender.host == "smtp.test.com"
    assert sender.port == 25
    assert sender.username == "user"
    assert sender.password == "pass"
    assert not sender.use_tls


def test_init_with_env_vars(monkeypatch):
    """Test initialization using environment variables."""
    env_vars = {
        "SMTP_HOST": "env.smtp.com",
        "SMTP_PORT": "2525",
        "SMTP_USERNAME": "env_user",
        "SMTP_PASSWORD": "env_pass",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    sender = EmailSender()
    assert sender.host == "env.smtp.com"
    assert sender.port == 2525
    assert sender.username == "env_user"
    assert sender.password == "env_pass"


def test_init_defaults():
    """Test initialization with default values."""
    sender = EmailSender()
    assert sender.host == "localhost"
    assert sender.port == 587
    assert sender.username is None
    assert sender.password is None
    assert sender.use_tls is True


def test_send_report_success(email_sender, mock_smtp, tmp_path):
    """Test successful report sending."""
    # Create a test file
    test_file = tmp_path / "test_report.txt"
    test_file.write_text("Test report content")

    result = email_sender.send_report(
        from_addr="from@example.com",
        to_addr="to@example.com",
        subject="Test Report",
        body="Here's your report",
        attachment_path=str(test_file),
        mime_type="text/plain",
    )

    assert result is True
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once_with("test@example.com", "password123")
    mock_smtp.send_message.assert_called_once()

    # Verify the sent message
    sent_msg = mock_smtp.send_message.call_args[0][0]
    assert isinstance(sent_msg, MIMEMultipart)
    assert sent_msg["From"] == "from@example.com"
    assert sent_msg["To"] == "to@example.com"
    assert sent_msg["Subject"] == "Test Report"


def test_send_report_without_auth(mock_smtp, tmp_path):
    """Test sending report without authentication."""
    sender = EmailSender(host="smtp.test.com", port=25, use_tls=False)
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = sender.send_report(
        "from@test.com",
        "to@test.com",
        "Subject",
        "Body",
        str(test_file),
        "text/plain",
    )

    assert result is True
    mock_smtp.starttls.assert_not_called()
    mock_smtp.login.assert_not_called()
    mock_smtp.send_message.assert_called_once()


@patch("smtplib.SMTP")
def test_send_report_failure(mock_smtp_class, email_sender, tmp_path):
    """Test handling of send failures."""
    mock_smtp_class.return_value.__enter__.return_value.send_message.side_effect = (
        Exception("Send failed")
    )
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = email_sender.send_report(
        "from@test.com",
        "to@test.com",
        "Subject",
        "Body",
        str(test_file),
        "text/plain",
    )

    assert result is False


def test_test_connection_success(mock_smtp, email_sender):
    """Test successful connection test."""
    assert email_sender.test_connection() is True
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once()


@patch("smtplib.SMTP")
def test_test_connection_failure(mock_smtp_class, email_sender):
    """Test failed connection test."""
    mock_smtp_class.return_value.__enter__.side_effect = Exception("Connection failed")
    assert email_sender.test_connection() is False
