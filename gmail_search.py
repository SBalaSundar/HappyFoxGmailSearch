import os
import json
import base64
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import db

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Authenticate with Gmail API using OAuth and return a service object.
    
    Returns:
        googleapiclient.discovery.Resource: Authenticated Gmail API service instance.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def fetch_emails(service):
    """Fetch the latest emails from the user's inbox.
    
    Args:
        service (googleapiclient.discovery.Resource): Authenticated Gmail API service instance.
    
    Returns:
        list: List of email message IDs.
    """
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
    messages = results.get('messages', [])
    return messages

def get_email_details(service, msg_id):
    """Retrieve details of an email by message ID.
    
    Args:
        service (googleapiclient.discovery.Resource): Authenticated Gmail API service instance.
        msg_id (str): The message ID of the email.
    
    Returns:
        dict: A dictionary containing email details (id, subject, sender, body, received_date).
    """
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
    date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
    received_date = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S') if date_str else None
    body = ''
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    return {'id': msg_id, 'subject': subject, 'sender': sender, 'body': body, 'received_date': received_date}

def store_email(email):
    """Store email details in the database.
    
    Args:
        email (dict): A dictionary containing email details.
    """
    conn = db.get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO emails (id, sender, subject, body, received_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    ''', (email['id'], email['sender'], email['subject'], email['body'], email['received_date']))
    conn.commit()
    conn.close()

def load_rules():
    """Load email processing rules from a JSON file.
    
    Returns:
        list: List of rules loaded from JSON.
    """
    with open('rules.json', 'r') as file:
        return json.load(file)['rules']

def apply_rules(email, rules):
    """Apply predefined rules to an email and trigger actions if conditions are met.
    
    Args:
        email (dict): The email details.
        rules (list): List of rules to apply.
    """
    for rule in rules:
        conditions_met = []
        for condition in rule['conditions']:
            field_value = email.get(condition['field'].lower().replace(' ', '_'), '')
            if condition['predicate'] == 'contains' and condition['value'].lower() in field_value.lower():
                conditions_met.append(True)
            elif condition['predicate'] == 'equals' and condition['value'].lower() == field_value.lower():
                conditions_met.append(True)
            elif condition['predicate'] == 'less_than':
                days_old = (datetime.now() - email['received_date']).days
                if days_old < int(condition['value']):
                    conditions_met.append(True)
        if (rule['condition_type'] == 'All' and all(conditions_met)) or (rule['condition_type'] == 'Any' and any(conditions_met)):
            perform_actions(email['id'], rule['actions'])

def perform_actions(email_id, actions):
    """Perform actions such as marking emails as read or moving to folders based on rules.
    
    Args:
        email_id (str): The ID of the email.
        actions (list): List of actions to perform.
    """
    service = authenticate_gmail()
    for action in actions:
        if action == 'mark_as_read':
            service.users().messages().modify(userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()
            logging.info(f'Email {email_id} marked as read')
        elif action.startswith('move_to_folder:'):
            label_name = action.split(':')[1]
            labels = service.users().labels().list(userId='me').execute().get('labels', [])
            label_id = next((lbl['id'] for lbl in labels if lbl['name'].lower() == label_name.lower()), None)
            if label_id:
                service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [label_id]}).execute()
                logging.info(f'Email {email_id} moved to {label_name}')

def main():
    """Main function to authenticate, fetch emails, store them, and apply rules."""
    logging.info('Starting Gmail Rule Processor...')
    service = authenticate_gmail()
    db.setup_database()
    rules = load_rules()
    messages = fetch_emails(service)
    for msg in messages:
        email = get_email_details(service, msg['id'])
        store_email(email)
        apply_rules(email, rules)
    logging.info('Processing complete.')

if __name__ == '__main__':
    main()