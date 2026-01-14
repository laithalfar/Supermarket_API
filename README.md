# Supermarket Management System API

A comprehensive REST API for managing supermarket operations including customers, employees, products, branches, and transactions.

## 🚀 Features

- **Customer Management**: Create, read, update, and delete customer records
- **Employee Management**: Manage employee information and roles
- **Product Management**: Track products, stock levels, and pricing
- **Branch Management**: Manage multiple supermarket branches
- **Transaction Processing**: Handle sales transactions with detailed line items
- **Authentication**: Login system for customers and employees

## 📁 Project Structure

```
supermarket/
├── src/
│   ├── api/
│   │   └── routers/          # API endpoint routers
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── customers.py  # Customer endpoints
│   │       ├── employees.py  # Employee endpoints
│   │       ├── products.py   # Product endpoints
│   │       ├── branches.py   # Branch endpoints
│   │       └── transactions.py
│   ├── crud/
│   │   └── CRUD.py          # Database operations
│   ├── model/
│   │   └── MODEL.py         # Pydantic models
│   └── factory/
│       └── run.py           # Application factory
├── frontend/                 # Frontend HTML/CSS/JS files
├── scripts/                  # Utility and maintenance scripts
├── tests/                    # Test files
├── docs/                     # Documentation
├── main.py                  # Application entry point
├── database_schema.sql      # Database schema definition
└── requirements.txt         # Python dependencies
```

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd supermarket
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=Supermarket
DB_POOL_SIZE=5
```

5. **Initialize the database**
```bash
mysql -u root -p < database_schema.sql
```

6. **Run migrations (if needed)**
```bash
python scripts/add_password_migration.py
```

## 🚀 Running the Application

**Development mode:**
```bash
python main.py
```

**Or using uvicorn directly:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Docs (Swagger)**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Customer Portal**: http://localhost:8000/shop
- **Admin Panel**: http://localhost:8000/admin

## 📚 API Documentation

### Authentication
- `POST /api/v1/auth/login` - Login for customers and employees

### Customers
- `GET /api/v1/customers` - List all customers
- `POST /api/v1/customers` - Create a new customer
- `GET /api/v1/customers/{id}` - Get customer by ID
- `PATCH /api/v1/customers/{id}` - Update customer
- `DELETE /api/v1/customers/{id}` - Delete customer

### Employees
- `GET /api/v1/employees` - List all employees
- `POST /api/v1/employees` - Create a new employee
- `GET /api/v1/employees/{id}` - Get employee by ID
- `PATCH /api/v1/employees/{id}` - Update employee
- `DELETE /api/v1/employees/{id}` - Delete employee

### Products
- `GET /api/v1/products` - List all products
- `POST /api/v1/products` - Create a new product
- `GET /api/v1/products/{id}` - Get product by ID
- `PATCH /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Branches
- `GET /api/v1/branches` - List all branches
- `POST /api/v1/branches` - Create a new branch
- `GET /api/v1/branches/{id}` - Get branch by ID
- `PATCH /api/v1/branches/{id}` - Update branch
- `DELETE /api/v1/branches/{id}` - Delete branch

### Transactions
- `GET /api/v1/transactions` - List all transactions
- `POST /api/v1/transactions` - Create a new transaction
- `GET /api/v1/transactions/{id}` - Get transaction by ID

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run specific test files:
```bash
python tests/test_auth.py
python test_api.py
```

## 🔧 Utility Scripts

See [scripts/README.md](scripts/README.md) for detailed information about available utility scripts.

## ⚠️ Security Warnings

**Current Implementation Issues:**
- ⚠️ Passwords are stored in plain text
- ⚠️ No JWT token authentication
- ⚠️ No rate limiting
- ⚠️ CORS is set to allow all origins

**For Production:**
1. Implement password hashing (bcrypt/argon2)
2. Add JWT token-based authentication
3. Enable rate limiting
4. Configure CORS properly
5. Use HTTPS only
6. Add input validation and sanitization
7. Implement proper error handling
8. Add logging and monitoring

## 📝 Database Schema

The application uses MySQL with the following tables:
- **CUSTOMERS**: Customer information and authentication
- **EMPLOYEES**: Employee information and roles
- **PRODUCTS**: Product catalog with pricing and stock
- **BRANCHES**: Supermarket branch locations
- **TRANSACTIONS**: Sales transaction headers
- **TRANSACTION_DETAILS**: Transaction line items

See `database_schema.sql` for the complete schema definition.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

[Add your license information here]

## 📞 Support

For issues and questions, please create an issue in the repository.

---

**Built with FastAPI, Pydantic, and MySQL**
