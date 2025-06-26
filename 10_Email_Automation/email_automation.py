#!/usr/bin/env python3
"""
Email Automation Tool - A Python application for automating email tasks.
"""

import os
import json
import smtplib
import logging
import time
import datetime
import schedule
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from pathlib import Path
from typing import List, Dict, Union, Optional, Any

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False


class EmailSender:
    """
    A class to handle email sending operations with various features like
    templates, scheduling, and attachments.
    """
    
    def __init__(self, config_file: str = 'config.json'):
        """
        Initialize the EmailSender with configuration from a JSON file.
        
        Args:
            config_file: Path to the configuration JSON file
        """
        self.logger = self._setup_logger()
        self.config = self._load_config(config_file)
        self.scheduled_jobs = []
        
        # Setup Jinja2 environment for templates if available
        if JINJA_AVAILABLE and 'template_dir' in self.config:
            template_dir = self.config['template_dir']
            if not os.path.exists(template_dir):
                os.makedirs(template_dir)
            self.jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            self.jinja_env = None
            if 'template_dir' in self.config:
                self.logger.warning("Jinja2 not available. Template features disabled.")
    
    def _setup_logger(self) -> logging.Logger:
        """Set up and configure the logger."""
        logger = logging.getLogger('email_automation')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # File handler
        file_handler = logging.FileHandler('logs/email_automation.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to the configuration JSON file
            
        Returns:
            Dictionary containing configuration values
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            required_fields = ['smtp_server', 'smtp_port', 'email', 'password']
            for field in required_fields:
                if field not in config:
                    self.logger.error(f"Missing required field in config: {field}")
                    raise ValueError(f"Missing required field in config: {field}")
                    
            return config
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {config_file}")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in configuration file: {config_file}")
            raise
    
    def _create_message(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        sender: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        is_html: bool = False
    ) -> MIMEMultipart:
        """
        Create an email message with all components.
        
        Args:
            subject: Email subject
            body: Email body content
            recipients: List of recipient email addresses
            cc: List of CC recipient email addresses
            bcc: List of BCC recipient email addresses
            sender: Sender email address (uses default from config if None)
            attachments: List of file paths to attach
            is_html: Whether the body content is HTML
            
        Returns:
            Prepared email message object
        """
        message = MIMEMultipart()
        message['Subject'] = subject
        
        # Set sender
        if sender is None:
            sender = self.config.get('default_sender', self.config['email'])
        
        if '<' in sender and '>' in sender:
            message['From'] = sender
        else:
            message['From'] = formataddr(("Sender", sender))
            
        message['To'] = ', '.join(recipients)
        
        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)
        
        # Attach body
        content_type = 'html' if is_html else 'plain'
        message.attach(MIMEText(body, content_type))
        
        # Add attachments
        if attachments:
            for attachment_path in attachments:
                try:
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    filename = os.path.basename(attachment_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}',
                    )
                    message.attach(part)
                    self.logger.info(f"Attached file: {filename}")
                except FileNotFoundError:
                    self.logger.error(f"Attachment file not found: {attachment_path}")
                    raise
        
        return message
    
    def send_email(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        sender: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        is_html: bool = False
    ) -> bool:
        """
        Send an email with the specified parameters.
        
        Args:
            subject: Email subject
            body: Email body content
            recipients: List of recipient email addresses
            cc: List of CC recipient email addresses
            bcc: List of BCC recipient email addresses
            sender: Sender email address (uses default from config if None)
            attachments: List of file paths to attach
            is_html: Whether the body content is HTML
            
        Returns:
            Boolean indicating success or failure
        """
        if not recipients:
            self.logger.error("No recipients specified")
            return False
            
        try:
            message = self._create_message(
                subject, body, recipients, cc, bcc, sender, attachments, is_html
            )
            
            # Get all recipients for SMTP
            all_recipients = recipients.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
                
            # Connect to SMTP server
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.config['email'], self.config['password'])
                server.send_message(message)
                
            self.logger.info(f"Email sent successfully to {len(all_recipients)} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_template_email(
        self,
        template_name: str,
        template_data: Dict[str, Any],
        subject: str,
        recipients: List[str],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        sender: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            template_name: Name of the template file
            template_data: Dictionary of data to render in the template
            subject: Email subject
            recipients: List of recipient email addresses
            cc: List of CC recipient email addresses
            bcc: List of BCC recipient email addresses
            sender: Sender email address (uses default from config if None)
            attachments: List of file paths to attach
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.jinja_env:
            self.logger.error("Template features are not available. Install Jinja2.")
            return False
            
        try:
            template = self.jinja_env.get_template(template_name)
            body = template.render(**template_data)
            
            return self.send_email(
                subject=subject,
                body=body,
                recipients=recipients,
                cc=cc,
                bcc=bcc,
                sender=sender,
                attachments=attachments,
                is_html=True
            )
        except Exception as e:
            self.logger.error(f"Template error: {str(e)}")
            return False
    
    def schedule_email(
        self,
        time: str,
        subject: str,
        body: str,
        recipients: List[str],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        sender: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        is_html: bool = False,
        recurring: str = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Schedule an email to be sent at a specific time.
        
        Args:
            time: Time string in format "HH:MM"
            subject: Email subject
            body: Email body content (ignored if template is provided)
            recipients: List of recipient email addresses
            cc: List of CC recipient email addresses
            bcc: List of BCC recipient email addresses
            sender: Sender email address (uses default from config if None)
            attachments: List of file paths to attach
            is_html: Whether the body content is HTML
            recurring: Schedule type ("daily", "weekly", "monthly", or None for one-time)
            template_name: Optional template name to use
            template_data: Optional template data
            
        Returns:
            Boolean indicating if scheduling was successful
        """
        try:
            # Create a job function
            def job():
                job_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                self.logger.info(f"Running scheduled email job {job_id}")
                
                if template_name and self.jinja_env:
                    self.send_template_email(
                        template_name=template_name,
                        template_data=template_data or {},
                        subject=subject,
                        recipients=recipients,
                        cc=cc,
                        bcc=bcc,
                        sender=sender,
                        attachments=attachments
                    )
                else:
                    self.send_email(
                        subject=subject,
                        body=body,
                        recipients=recipients,
                        cc=cc,
                        bcc=bcc,
                        sender=sender,
                        attachments=attachments,
                        is_html=is_html
                    )
            
            # Schedule the job
            if recurring == 'daily':
                scheduled_job = schedule.every().day.at(time).do(job)
            elif recurring == 'weekly':
                scheduled_job = schedule.every().week.at(time).do(job)
            elif recurring == 'monthly':
                # This is an approximation since schedule doesn't support monthly directly
                scheduled_job = schedule.every(30).days.at(time).do(job)
            else:
                # One-time schedule
                today = datetime.date.today()
                hour, minute = map(int, time.split(':'))
                schedule_time = datetime.datetime.combine(today, datetime.time(hour, minute))
                
                if schedule_time < datetime.datetime.now():
                    # If the time has passed today, schedule for tomorrow
                    schedule_time += datetime.timedelta(days=1)
                
                # Calculate seconds until the scheduled time
                delay = (schedule_time - datetime.datetime.now()).total_seconds()
                
                # Use a one-time job
                scheduled_job = schedule.every(delay).seconds.do(job)
                
            self.scheduled_jobs.append(scheduled_job)
            self.logger.info(f"Email scheduled for {time}" + 
                           (f" (recurring: {recurring})" if recurring else ""))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule email: {str(e)}")
            return False
    
    def run_scheduler(self, blocking: bool = True) -> None:
        """
        Run the scheduler to process scheduled emails.
        
        Args:
            blocking: Whether to run in blocking mode
        """
        self.logger.info("Starting email scheduler")
        
        if blocking:
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            # Run once and return
            schedule.run_pending()
    
    def create_template(self, template_name: str, content: str) -> bool:
        """
        Create a new email template.
        
        Args:
            template_name: Name of the template file
            content: HTML content of the template
            
        Returns:
            Boolean indicating success or failure
        """
        if not self.jinja_env:
            self.logger.error("Template features are not available. Install Jinja2.")
            return False
            
        try:
            template_dir = self.config['template_dir']
            template_path = os.path.join(template_dir, template_name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            with open(template_path, 'w') as f:
                f.write(content)
                
            self.logger.info(f"Template created: {template_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create template: {str(e)}")
            return False


def main():
    """
    Example usage of the EmailSender class.
    """
    # Check if config.json exists, if not create a sample one
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
        
        print("Please edit config.json with your email settings before running.")
        return
    
    sender = EmailSender('config.json')
    
    # Example: Create a template
    if JINJA_AVAILABLE:
        template_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { background-color: #4CAF50; color: white; padding: 10px; }
                .content { padding: 20px; }
                .footer { font-size: 12px; color: #888; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome, {{ name }}!</h1>
            </div>
            <div class="content">
                <p>Thank you for joining {{ company }}.</p>
                <p>Your account has been created successfully.</p>
                <p>Here are your account details:</p>
                <ul>
                    <li>Username: {{ username }}</li>
                    <li>Email: {{ email }}</li>
                </ul>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        os.makedirs('templates', exist_ok=True)
        sender.create_template('welcome.html', template_content)
    
    # Interactive menu
    while True:
        print("\nEmail Automation Tool")
        print("1. Send a simple email")
        print("2. Send an email with attachment")
        print("3. Send a template email")
        print("4. Schedule an email")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            subject = input("Subject: ")
            body = input("Body: ")
            recipients = input("Recipients (comma separated): ").split(',')
            
            if sender.send_email(subject, body, recipients):
                print("Email sent successfully!")
            else:
                print("Failed to send email.")
                
        elif choice == '2':
            subject = input("Subject: ")
            body = input("Body: ")
            recipients = input("Recipients (comma separated): ").split(',')
            attachment_path = input("Path to attachment: ")
            
            if sender.send_email(subject, body, recipients, attachments=[attachment_path]):
                print("Email with attachment sent successfully!")
            else:
                print("Failed to send email.")
                
        elif choice == '3':
            if not JINJA_AVAILABLE:
                print("Jinja2 is not installed. Cannot use templates.")
                continue
                
            template_name = input("Template name: ")
            subject = input("Subject: ")
            recipients = input("Recipients (comma separated): ").split(',')
            
            # Simple template data collection
            print("Enter template data (empty key to finish):")
            template_data = {}
            while True:
                key = input("Key: ")
                if not key:
                    break
                value = input(f"Value for {key}: ")
                template_data[key] = value
            
            if sender.send_template_email(template_name, template_data, subject, recipients):
                print("Template email sent successfully!")
            else:
                print("Failed to send template email.")
                
        elif choice == '4':
            time = input("Time (HH:MM): ")
            subject = input("Subject: ")
            body = input("Body: ")
            recipients = input("Recipients (comma separated): ").split(',')
            recurring = input("Recurring (daily/weekly/monthly/none): ").lower()
            
            if recurring not in ['daily', 'weekly', 'monthly']:
                recurring = None
                
            if sender.schedule_email(time, subject, body, recipients, recurring=recurring):
                print(f"Email scheduled for {time}" + 
                     (f" (recurring: {recurring})" if recurring else ""))
                
                run_scheduler = input("Start scheduler now? (y/n): ").lower()
                if run_scheduler == 'y':
                    print("Running scheduler. Press Ctrl+C to stop.")
                    try:
                        sender.run_scheduler()
                    except KeyboardInterrupt:
                        print("\nScheduler stopped.")
            else:
                print("Failed to schedule email.")
                
        elif choice == '5':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 