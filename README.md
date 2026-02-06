sudo apt install tesseract-ocr tesseract-ocr-tam poppler-utils
# ECI Election Stats & Info System

A premium Streamlit application for tracking election statistics, party alliances, and candidate profiles.

## Features
- **Admin Dashboard**: Manage alliances, parties, and candidates.
- **User Dashboard**: View election statistics and detailed candidate profiles.
- **Authentication**: Secure login and signup system with role-based access control.
- **Database**: PostgreSQL integration for persistent data storage.
- **Modern UI**: Glassmorphism design with responsiveness.

## Prerequisites
- Python 3.8+
- PostgreSQL server

## Setup
1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Database Configuration**:
    - Update the database credentials in `database.py` (DB_USER, DB_PASSWORD, etc.).
    - Or set environment variables: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.

3.  **Initialize Database**:
    ```bash
    python setup_db.py
    ```

4.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

## Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`