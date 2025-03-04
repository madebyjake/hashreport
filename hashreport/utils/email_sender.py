"""This module provides the EmailSender class for sending emails with attachments."""

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


class EmailSender:
    """Handle email sending functionality."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
    ):
        """
        Initialize the EmailSender with SMTP server details.

        Args:
            host (Optional[str]): SMTP server host.
            port (Optional[int]): SMTP server port.
            username (Optional[str]): SMTP server username.
            password (Optional[str]): SMTP server password.
            use_tls (bool): Whether to use TLS for the connection.
        """
        if host:
            self.host = self._validate_hostname(host)
        else:
            self.host = os.environ.get("SMTP_HOST", "localhost")
        self.port = port or int(os.environ.get("SMTP_PORT", 587))
        self.username = username or os.environ.get("SMTP_USERNAME")
        self.password = password or os.environ.get("SMTP_PASSWORD")
        self.use_tls = use_tls

    @staticmethod
    def _validate_hostname(hostname: str) -> str:
        """Validate and sanitize hostname."""
        import re

        if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", hostname):
            raise ValueError("Invalid hostname format")
        return hostname

    def send_report(
        self,
        from_addr: str,
        to_addr: str,
        subject: str,
        body: str,
        attachment_path: str,
        mime_type: str,
    ) -> bool:
        """
        Send email with report attachment.

        Args:
            from_addr (str): Sender's email address.
            to_addr (str): Recipient's email address.
            subject (str): Subject of the email.
            body (str): Body of the email.
            attachment_path (str): Path to the attachment file.
            mime_type (str): MIME type of the attachment.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = from_addr
            msg["To"] = to_addr
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(attachment_path)}"',
            )
            part.add_header("Content-Type", mime_type)
            msg.attach(part)

            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def test_connection(self) -> bool:
        """
        Test SMTP connection and credentials.

        Returns:
            bool: True if the connection and credentials are valid, False otherwise.
        """
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
            return True
        except Exception as e:
            print(f"SMTP test failed: {str(e)}")
            return False
