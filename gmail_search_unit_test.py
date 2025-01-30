import unittest
import psycopg2
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import db
import gmail_search

class TestHappyFoxGmailScript(unittest.TestCase):
    
    @patch('psycopg2.connect')
    def test_setup_database(self, mock_connect):
        """Test if the database setup executes without errors.
        
        This test mocks the SQLite connection and verifies that the database
        table creation command is executed correctly and the connection
        commits changes.
        """
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        db.setup_database()
        mock_conn.cursor().execute.assert_called()
        mock_conn.commit.assert_called()

    @patch('psycopg2.connect')
    def test_store_email(self, mock_connect):
        """Test storing email data in the database.
        
        This test mocks the SQLite connection and ensures that an email entry
        is inserted correctly into the database with proper values.
        """
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        email = {
            'id': '123',
            'sender': 'test@example.com',
            'subject': 'Test Email',
            'body': 'This is a test email.',
            'received_date': '2025-01-01 12:00:00'
        }
        gmail_search.store_email(email)
        mock_conn.cursor().execute.assert_called()
        mock_conn.commit.assert_called()
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"rules": [{"conditions": [{"field": "Subject", "predicate": "contains", "value": "Test"}], "condition_type": "All", "actions": ["mark_as_read"]}]}')
    def test_load_rules(self, mock_open):
        """Test loading rules from JSON file.
        
        This test mocks the open function and verifies that rules are correctly
        loaded from a predefined JSON string and parsed into a list of rules.
        """
        rules = gmail_search.load_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['actions'][0], 'mark_as_read')
    
    @patch('gmail_search.perform_actions')
    def test_apply_rules(self, mock_perform_actions):
        """Test applying rules to emails.
        
        This test checks that rules are correctly applied to emails by verifying
        that actions are triggered when conditions match. It ensures that
        `perform_actions` is called with the expected email ID and actions.
        """
        email = {
            'id': '123',
            'sender': 'test@example.com',
            'subject': 'Test Email',
            'body': 'This is a test email.',
            'received_date': datetime.now() - timedelta(days=1)
        }
        rules = [{
            "conditions": [{"field": "Subject", "predicate": "contains", "value": "Test"}],
            "condition_type": "All",
            "actions": ["mark_as_read"]
        }]
        gmail_search.apply_rules(email, rules)
        mock_perform_actions.assert_called_with('123', ['mark_as_read'])
    
if __name__ == '__main__':
    unittest.main()
