# Email Automation Tool

A Python application for automating email tasks such as sending scheduled emails, processing email templates, and handling attachments.

## Features

- Send emails with plain text or HTML content
- Support for email templates with variable substitution
- Schedule emails to be sent at specific times
- Send emails to multiple recipients (To, CC, BCC)
- Attach files to emails
- Email queue management
- Logging of email activities

## Requirements

- Python 3.6+
- Required packages:
  - `smtplib` (built-in)
  - `email` (built-in)
  - `schedule`
  - `jinja2` (for template processing)

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install schedule jinja2
   ```
3. Configure your email settings in `config.json`

## Usage

### Basic Usage

```python
from email_automation import EmailSender

# Initialize the sender
sender = EmailSender('config.json')

# Send a simple email
sender.send_email(
    subject="Test Email",
    body="This is a test email sent from the Email Automation tool.",
    recipients=["recipient@example.com"]
)
```

### Using Templates

```python
# Send an email using a template
sender.send_template_email(
    template_name="welcome.html",
    template_data={"username": "John", "company": "ACME Inc."},
    subject="Welcome to Our Service",
    recipients=["new_user@example.com"]
)
```

### Scheduling Emails

```python
# Schedule an email to be sent daily at 9:00 AM
sender.schedule_email(
    time="09:00",
    subject="Daily Report",
    body="Here is your daily report.",
    recipients=["manager@example.com"],
    attachments=["reports/daily_report.pdf"],
    recurring="daily"
)

# Start the scheduler
sender.run_scheduler()
```

## Configuration

Create a `config.json` file with the following structure:

```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "your_email@gmail.com",
    "password": "your_app_password",
    "default_sender": "Your Name <your_email@gmail.com>",
    "template_dir": "templates/"
}
```

**Note:** For Gmail, you need to use an App Password instead of your regular password. See [Google Account Help](https://support.google.com/accounts/answer/185833) for more information.

## Security Considerations

- Never commit your `config.json` file with real credentials to version control
- Consider using environment variables for sensitive information
- Use secure SMTP connections (TLS/SSL)
- Be careful with email templates that might contain sensitive data

## License

This project is open source and available under the MIT License. 