#!/usr/bin/env python3
"""
Bulk Email Sender - A tool for sending emails to multiple recipients from a CSV file.
"""

import csv
import argparse
import time
from email_automation import EmailSender

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Send bulk emails from a CSV file")
    parser.add_argument("csv_file", help="Path to the CSV file containing recipient data")
    parser.add_argument("--template", help="Email template file to use", default=None)
    parser.add_argument("--subject", help="Email subject", required=True)
    parser.add_argument("--body", help="Text file containing email body (if not using template)", default=None)
    parser.add_argument("--config", help="Path to config file", default="config.json")
    parser.add_argument("--delay", help="Delay between emails in seconds", type=int, default=1)
    parser.add_argument("--test", help="Send only to the first recipient as a test", action="store_true")
    parser.add_argument("--dry-run", help="Don't actually send emails, just show what would be sent", action="store_true")
    return parser.parse_args()

def read_csv(csv_file):
    """Read recipient data from a CSV file."""
    recipients = []
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipients.append(row)
        return recipients
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def read_body_file(body_file):
    """Read email body from a text file."""
    try:
        with open(body_file, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading body file: {e}")
        return ""

def main():
    """Main function to send bulk emails."""
    args = parse_arguments()
    
    # Read recipient data
    recipients = read_csv(args.csv_file)
    if not recipients:
        print("No recipients found or error reading CSV file.")
        return
    
    # Read email body if provided
    body = ""
    if args.body:
        body = read_body_file(args.body)
        if not body:
            print("Error reading email body file.")
            return
    
    # Initialize email sender
    try:
        sender = EmailSender(args.config)
    except Exception as e:
        print(f"Error initializing email sender: {e}")
        return
    
    # Limit to first recipient if test mode
    if args.test:
        recipients = recipients[:1]
        print("TEST MODE: Sending only to the first recipient")
    
    # Process each recipient
    print(f"Preparing to send emails to {len(recipients)} recipients...")
    
    for i, recipient in enumerate(recipients):
        # Extract email address (assuming the CSV has an 'email' column)
        if 'email' not in recipient:
            print(f"Error: Row {i+1} does not have an 'email' column")
            continue
        
        email = recipient['email']
        print(f"Processing {i+1}/{len(recipients)}: {email}")
        
        try:
            if args.template:
                # Send using template
                if args.dry_run:
                    print(f"  Would send template email to {email} with data: {recipient}")
                else:
                    success = sender.send_template_email(
                        template_name=args.template,
                        template_data=recipient,
                        subject=args.subject,
                        recipients=[email]
                    )
                    if success:
                        print(f"  Email sent successfully to {email}")
                    else:
                        print(f"  Failed to send email to {email}")
            else:
                # Send regular email
                if args.dry_run:
                    print(f"  Would send regular email to {email}")
                else:
                    # Replace placeholders in the body with recipient data
                    personalized_body = body
                    for key, value in recipient.items():
                        personalized_body = personalized_body.replace(f"{{{{{key}}}}}", value)
                    
                    success = sender.send_email(
                        subject=args.subject,
                        body=personalized_body,
                        recipients=[email],
                        is_html='<html' in personalized_body.lower()
                    )
                    if success:
                        print(f"  Email sent successfully to {email}")
                    else:
                        print(f"  Failed to send email to {email}")
                        
            # Add delay between emails
            if i < len(recipients) - 1 and not args.dry_run:
                print(f"  Waiting {args.delay} seconds before sending next email...")
                time.sleep(args.delay)
                
        except Exception as e:
            print(f"  Error processing recipient {email}: {e}")
    
    print("Bulk email process completed!")

if __name__ == "__main__":
    main() 