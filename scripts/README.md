# Utility Scripts

This directory contains utility scripts for database management, debugging, and maintenance.

## Database Management Scripts

### `add_password_migration.py`
Adds password columns to CUSTOMERS and EMPLOYEES tables if they don't exist.

**Usage:**
```bash
python scripts/add_password_migration.py
```

**Purpose:** Safely migrates the database schema to include password fields for authentication.

---

### `fix_schema.py`
Rebuilds the TRANSACTION_DETAILS table with the correct schema.

**Usage:**
```bash
python scripts/fix_schema.py
```

**Warning:** This script drops and recreates the TRANSACTION_DETAILS table. Use with caution in production.

---

### `fix_products.py`
Checks for and fixes invalid product data (negative prices, costs, or stock).

**Usage:**
```bash
python scripts/fix_products.py
```

**Purpose:** Data validation and cleanup for the PRODUCTS table.

---

## Debugging Scripts

### `check_db.py`
Displays comprehensive information about all database tables.

**Usage:**
```bash
python scripts/check_db.py
```

**Output:** Prints table structures and row counts to console.

---

### `check_db_to_file.py`
Exports database information to a file for review.

**Usage:**
```bash
python scripts/check_db_to_file.py
```

**Output:** Creates `db_report.txt` with database schema and data.

---

### `debug_users.py`
Exports customer and employee data to JSON for debugging.

**Usage:**
```bash
python scripts/debug_users.py
```

**Output:** Creates `users_output.json` with user information.

**Warning:** This script exports passwords. Do not share the output file.

---

### `dump_products.py`
Displays all products from the database.

**Usage:**
```bash
python scripts/dump_products.py
```

**Note:** This script uses SQLite. Update it to use MySQL for the current database.

---

## Security Notice

⚠️ **Important:** These scripts contain database credentials and may expose sensitive data. 

- Never commit output files to version control
- Use environment variables for credentials in production
- Restrict access to these scripts in production environments

## Configuration

All scripts use the following database configuration:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0798628195Far",  # Should be in .env file
    "database": "Supermarket",
}
```

**Recommendation:** Update scripts to use environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "Supermarket"),
}
```
