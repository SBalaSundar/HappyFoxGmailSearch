# Gmail Search Script

This project implements a Python script that integrates with the Gmail API to fetch emails, store them in a database, and process them based on predefined rules. It also includes unit tests to validate the core functionalities.

## Features
- Authenticate and interact with Gmail API using OAuth 2.0
- Fetch emails from the inbox and store them in an SQLite database
- Process emails based on rules defined in a JSON file
- Apply actions such as marking emails as read or moving them to specific folders
- Unit tests for database operations, rule application, and API interactions

## Prerequisites
Before running the script, ensure you have the following installed:
- Python 3.7+
- `pip install -r requirements.txt` (for dependencies)
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials (`credentials.json` file)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Gmail API Authentication
- Obtain `credentials.json` from Google Developer Console
- Place `credentials.json` in the project root directory
- Run the script once to authenticate and generate `token.pickle`

### 4. Create SQLite Database
```bash
python -c "import gmail_search; gmail_search.setup_database()"
```

### 5. Define Email Processing Rules
Edit the `rules.json` file to specify email filtering rules. Example:
```json
{
  "rules": [
    {
      "conditions": [
        { "field": "From", "predicate": "contains", "value": "example.com" },
        { "field": "Subject", "predicate": "contains", "value": "Invoice" }
      ],
      "condition_type": "All",
      "actions": ["mark_as_read"]
    }
  ]
}
```

## Running the Script
To fetch and process emails:
```bash
python gmail_search.py
```

## Running Unit Tests
To execute the unit tests:
```bash
python -m unittest gmail_search_unit_test.py
```

## Project Structure
```
.
├── gmail_search.py              # Main script
├── gmail_search_unit_test.py    # Unit tests
├── rules.json                   # Email filtering rules
├── credentials.json             # OAuth 2.0 credentials (not included in repo)
├── token.pickle                 # Stored authentication token (generated at runtime)
├── requirements.txt             # Required dependencies
├── README.md                    # Documentation
```

