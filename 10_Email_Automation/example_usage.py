 #!/usr/bin/env python3
"""
Example usage of the Email Automation Tool.
This script demonstrates various features of the email automation library.
"""

import os
import json
import datetime
from email_automation import EmailSender

def setup_config():
    """Create a sample config file if it doesn't exist."""
    if not os.path.exists('config.json'):
        print("Creating sample config.json file...")
        sample_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "your_email@gmail.com",
            "password": "your_app_password",
            "default_sender": "Your Name <your_email@gmail.com>",
            "template_dir": "templates/"
        }
        
        with open('config.json', 'w') as f:
            json.dump(sample_config, f, indent=4)
        
        print("Please edit config.json with your email settings before running examples.")
        return False
    return True

def example_simple_email(sender):
    """Send a simple plain text email."""
    print("\n=== Sending a Simple Email ===")
    
    success = sender.send_email(
        subject="Test Email from Python",
        body="This is a test email sent from the Email Automation tool.\n\nRegards,\nPython Script",
        recipients=["recipient@example.com"]
    )
    
    if success:
        print("Simple email sent successfully!")
    else:
        print("Failed to send simple email.")

def example_html_email(sender):
    """Send an HTML email."""
    print("\n=== Sending an HTML Email ===")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1 style="color: #4285f4;">HTML Email Test</h1>
        <p>This is a <b>test email</b> with <span style="color: #ea4335;">HTML formatting</span>.</p>
        <p>Here's a list of features:</p>
        <ul>
            <li>HTML formatting</li>
            <li>Styled text</li>
            <li>Lists and other elements</li>
        </ul>
        <p>Regards,<br>Python Script</p>
    </body>
    </html>
    """
    
    success = sender.send_email(
        subject="HTML Email Test",
        body=html_content,
        recipients=["recipient@example.com"],
        is_html=True
    )
    
    if success:
        print("HTML email sent successfully!")
    else:
        print("Failed to send HTML email.")

def example_email_with_attachment(sender):
    """Send an email with an attachment."""
    print("\n=== Sending an Email with Attachment ===")
    
    # Create a sample file to attach
    with open("sample_attachment.txt", "w") as f:
        f.write("This is a sample attachment file.\n")
        f.write("It will be attached to the email.\n")
    
    success = sender.send_email(
        subject="Email with Attachment",
        body="This email has a text file attached to it.",
        recipients=["recipient@example.com"],
        attachments=["sample_attachment.txt"]
    )
    
    if success:
        print("Email with attachment sent successfully!")
    else:
        print("Failed to send email with attachment.")

def example_template_email(sender):
    """Send an email using a template."""
    print("\n=== Sending a Template Email ===")
    
    # Ensure templates directory exists
    os.makedirs("templates", exist_ok=True)
    
    # Template data
    template_data = {
        "username": "JohnDoe",
        "email": "johndoe@example.com",
        "company": "ACME Corporation",
        "account_type": "Premium",
        "verification_link": "https://example.com/verify?token=abc123",
        "current_year": datetime.datetime.now().year
    }
    
    success = sender.send_template_email(
        template_name="welcome.html",
        template_data=template_data,
        subject="Welcome to ACME Corporation",
        recipients=["johndoe@example.com"]
    )
    
    if success:
        print("Template email sent successfully!")
    else:
        print("Failed to send template email.")

def example_newsletter_email(sender):
    """Send a newsletter using a template."""
    print("\n=== Sending a Newsletter ===")
    
    # Newsletter data
    newsletter_data = {
        "company": "ACME Corporation",
        "newsletter_date": datetime.datetime.now().strftime("%B %d, %Y"),
        "recipient_name": "John Doe",
        "newsletter_frequency": "monthly",
        "articles": [
            {
                "title": "New Product Launch",
                "image_url": "https://via.placeholder.com/600x300",
                "summary": "We're excited to announce our latest product, the ACME RocketBoots 3000. These revolutionary boots will help you catch roadrunners with ease.",
                "link": "https://example.com/news/product-launch"
            },
            {
                "title": "Company Achieves Record Growth",
                "image_url": "https://via.placeholder.com/600x300",
                "summary": "ACME Corporation reports record growth in Q3, with revenue increasing by 25% compared to last year.",
                "link": "https://example.com/news/record-growth"
            }
        ],
        "events": [
            {
                "date": "October 15, 2023",
                "name": "ACME Annual Conference",
                "location": "Virtual Event"
            },
            {
                "date": "November 5, 2023",
                "name": "Product Demo Webinar",
                "location": "Online"
            }
        ],
        "social_links": {
            "facebook": "https://facebook.com/acmecorp",
            "twitter": "https://twitter.com/acmecorp",
            "linkedin": "https://linkedin.com/company/acmecorp",
            "instagram": "https://instagram.com/acmecorp"
        },
        "unsubscribe_link": "https://example.com/unsubscribe?email=johndoe@example.com",
        "preferences_link": "https://example.com/preferences?email=johndoe@example.com",
        "current_year": datetime.datetime.now().year
    }
    
    success = sender.send_template_email(
        template_name="newsletter.html",
        template_data=newsletter_data,
        subject="ACME Monthly Newsletter - " + newsletter_data["newsletter_date"],
        recipients=["johndoe@example.com"]
    )
    
    if success:
        print("Newsletter sent successfully!")
    else:
        print("Failed to send newsletter.")

def example_scheduled_email(sender):
    """Schedule an email to be sent."""
    print("\n=== Scheduling an Email ===")
    
    # Calculate a time 2 minutes from now
    now = datetime.datetime.now()
    schedule_time = (now + datetime.timedelta(minutes=2)).strftime("%H:%M")
    
    success = sender.schedule_email(
        time=schedule_time,
        subject="Scheduled Test Email",
        body="This email was scheduled to be sent 2 minutes after the script ran.",
        recipients=["recipient@example.com"]
    )
    
    if success:
        print(f"Email scheduled for {schedule_time}")
        print("Note: To actually send scheduled emails, you need to run the scheduler.")
        print("In a real application, you would call sender.run_scheduler() in a separate thread or process.")
    else:
        print("Failed to schedule email.")

def main():
    """Run the example functions."""
    if not setup_config():
        return
    
    print("Email Automation Tool - Example Usage")
    print("=====================================")
    print("Note: Before running these examples, make sure to:")
    print("1. Edit config.json with your email settings")
    print("2. Install required packages: pip install schedule jinja2")
    print("\nPress Enter to continue or Ctrl+C to exit...")
    input()
    
    try:
        # Initialize the email sender
        sender = EmailSender('config.json')
        
        # Run examples
        example_simple_email(sender)
        example_html_email(sender)
        example_email_with_attachment(sender)
        example_template_email(sender)
        example_newsletter_email(sender)
        example_scheduled_email(sender)
        
        print("\nAll examples completed!")
        print("To run the scheduler and send the scheduled email, you would call:")
        print("sender.run_scheduler()")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()