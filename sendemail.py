import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Protocol

# Constants
DEFAULT_EMAIL = "support@arjancodes.com"
LOGIN = "admin"
PASSWORD = "admin"


# Protocol Definition for SMTP Server
class EmailServer(Protocol):
    @property
    def _host(self) -> str:
        ...

    def connect(self, host: str, port: int) -> None:
        ...

    def starttls(self) -> None:
        ...

    def login(self, login: str, password: str) -> None:
        ...

    def quit(self) -> None:
        ...

    def sendmail(self, from_address: str, to_address: str, message: str) -> None:
        ...


# Concrete SMTP Server Class
class SmtpLibEmailServer:
    def __init__(self, host: str, port: int):
        self._host = f"{host}:{port}"
        self._connection = None

    def connect(self, host: str, port: int) -> None:
        print(f"Connecting to SMTP server {host}:{port}...")
        self._connection = smtplib.SMTP(host, port)
        self._connection.set_debuglevel(1)  # Enable detailed debug output for the SMTP session
        self._connection.ehlo()  # Extended SMTP greeting
        print("Connected to SMTP server.")

    def starttls(self) -> None:
        if self._connection:
            print("Starting TLS encryption...")
            self._connection.starttls()
            self._connection.ehlo()
            print("TLS encryption started.")

    def login(self, login: str, password: str) -> None:
        if self._connection:
            print(f"Logging in as {login}...")
            self._connection.login(login, password)
            print("Logged in successfully.")

    def quit(self) -> None:
        if self._connection:
            print("Quitting SMTP server...")
            self._connection.quit()
            self._connection = None
            print("Disconnected from SMTP server.")

    def sendmail(self, from_address: str, to_address: str, message: str) -> None:
        if self._connection:
            print(f"Sending email from {from_address} to {to_address}...")
            self._connection.sendmail(from_address, to_address, message)
            print("Email sent successfully.")


# Email Client Class
class EmailClient:
    def __init__(
        self,
        smtp_server: EmailServer,
        login: str | None = None,
        password: str | None = None,
        name: str | None = None,
        to_address: str = DEFAULT_EMAIL,
    ):
        self._server = smtp_server
        host, port = str(smtp_server._host).split(":")  # type: ignore
        self._host: str = host
        self._port = int(port)
        if not login or not password:
            self._login, self._password = LOGIN, PASSWORD
        else:
            self._login, self._password = login, password
        self.name = name
        self.to_address = to_address

    def _connect(self) -> None:
        try:
            self._server.connect(self._host, self._port)
            self._server.starttls()
            self._server.login(self._login, self._password)
        except Exception as e:
            print(f"Failed to connect to SMTP server: {e}")
            raise

    def _quit(self) -> None:
        try:
            self._server.quit()
        except Exception as e:
            print(f"Failed to disconnect from SMTP server: {e}")

    def send_message(
        self,
        from_address: str,
        to_address: str,
        subject: str = "No subject",
        message: str = "",
    ) -> None:
        try:
            print("Preparing email message...")
            msg = MIMEMultipart()
            msg["From"] = from_address
            if not to_address:
                to_address = self.to_address
            msg["To"] = to_address
            msg["Subject"] = subject
            mime = MIMEText(
                message,
                "html" if message.lower().startswith("<!doctype html>") else "plain",
            )
            msg.attach(mime)

            print("Connecting to server to send email...")
            self._connect()
            print(f"Sending email to {to_address}...")
            self._server.sendmail(from_address, to_address, msg.as_string())
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            print("Disconnecting from SMTP server...")
            self._quit()


# Main Function to Test the Email Client with Gmail
if __name__ == "__main__":
    # Gmail Configuration
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    LOGIN = "niledatahub@gmail.com"  # Replace with your Gmail address
    PASSWORD = "sadfsfsdfdsdsfsdfdsfsd"  # Replace with your App Password generated in Gmail

    # Create a concrete SMTP server instance
    smtp_server = SmtpLibEmailServer(SMTP_HOST, SMTP_PORT)

    # Create an email client with the SMTP server
    email_client = EmailClient(smtp_server, login=LOGIN, password=PASSWORD)

    # Send a message using the email client
    try:
        email_client.send_message(
            from_address="niledatahub@gmail.com",  # Replace with your Gmail address
            to_address="ama66@cornell.edu",  # Replace with the recipient's email address
            subject="Test Email",
            message="This is a test email sent via Gmail SMTP."
        )
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
