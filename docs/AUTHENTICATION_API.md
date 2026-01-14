# Authentication API Documentation

## Overview
The Supermarket Management System now includes secure user authentication with signup and login capabilities for both customers and employees.

## Security Features
- **Argon2 Password Hashing** - Industry-standard password encryption
- **Password Strength Validation** - Enforces strong password requirements
- **Secure Verification** - Constant-time password comparison

## Endpoints

### 1. Customer Signup
Create a new customer account.

**Endpoint:** `POST /api/v1/auth/signup/customer`

**Request Body:**
```json
{
  "name": "string (1-100 characters)",
  "email": "valid email address",
  "password": "string (min 8 chars, 1 uppercase, 1 lowercase, 1 digit)",
  "age": "integer (1-119)",
  "membership": "boolean (optional, default: false)"
}
```

**Success Response (201):**
```json
{
  "id": 1,
  "name": "John Doe",
  "role": "customer",
  "email": "john@example.com",
  "message": "Customer account created successfully"
}
```

**Error Responses:**
- `400` - Weak password or duplicate email
- `500` - Server error

---

### 2. Employee Signup
Create a new employee account.

> **Note:** In production, this endpoint should require admin authentication.

**Endpoint:** `POST /api/v1/auth/signup/employee`

**Request Body:**
```json
{
  "name": "string (1-100 characters)",
  "email": "valid email address",
  "password": "string (min 8 chars, 1 uppercase, 1 lowercase, 1 digit)",
  "age": "integer (1-119)",
  "role": "string (ADMIN, CASHIER, etc.)",
  "dateOfEmployment": "string (YYYY-MM-DD format)"
}
```

**Success Response (201):**
```json
{
  "id": 1,
  "name": "Jane Smith",
  "role": "CASHIER",
  "email": "jane@example.com",
  "message": "Employee account created successfully"
}
```

**Error Responses:**
- `400` - Weak password or duplicate email
- `500` - Server error

---

### 3. Login
Authenticate a user (customer or employee).

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "email": "valid email address",
  "password": "string",
  "role": "customer | admin"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "name": "John Doe",
  "role": "customer",
  "email": "john@example.com",
  "message": "Login successful"
}
```

**Error Responses:**
- `401` - Invalid email or password

---

## Password Requirements

All passwords must meet the following criteria:
- ✅ Minimum 8 characters long
- ✅ At least one uppercase letter (A-Z)
- ✅ At least one lowercase letter (a-z)
- ✅ At least one digit (0-9)

**Examples:**
- ✅ `SecurePass123`
- ✅ `MyPassword1`
- ❌ `password` (no uppercase, no digit)
- ❌ `PASSWORD123` (no lowercase)
- ❌ `Pass1` (too short)

---

## Example Usage

### Using cURL

**Create Customer:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup/customer \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "password": "SecurePass123",
    "age": 25,
    "membership": true
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123",
    "role": "customer"
  }'
```

### Using JavaScript (Fetch API)

**Create Customer:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/signup/customer', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Alice Johnson',
    email: 'alice@example.com',
    password: 'SecurePass123',
    age: 25,
    membership: true
  })
});

const data = await response.json();
console.log(data);
```

**Login:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'alice@example.com',
    password: 'SecurePass123',
    role: 'customer'
  })
});

const data = await response.json();
console.log(data);
```

---

## Security Notes

### Password Storage
- Passwords are hashed using **Argon2** (winner of the Password Hashing Competition)
- Plain text passwords are never stored in the database
- Hashes are salted automatically by Argon2

### Migration
If you have existing accounts with plain text passwords, run the migration script:
```bash
python scripts/migrate_passwords_to_argon2.py
```

### Best Practices
1. Always use HTTPS in production
2. Implement rate limiting on auth endpoints
3. Add JWT token authentication for session management
4. Require admin authentication for employee signup
5. Implement email verification for new accounts

---

## Interactive API Documentation

Visit the interactive API documentation at:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

You can test all endpoints directly from the browser!
