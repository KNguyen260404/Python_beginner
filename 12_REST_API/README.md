# REST API Project

A simple yet powerful REST API built with Flask, SQLAlchemy, and JWT authentication.

## Features

- RESTful endpoints for CRUD operations
- JWT-based authentication
- Input validation
- Database integration with SQLAlchemy
- Error handling
- API documentation with Swagger
- Rate limiting
- Pagination for list endpoints
- Filtering and sorting
- Comprehensive logging

## Project Structure

```
12_REST_API/
├── app/
│   ├── __init__.py          # Flask application initialization
│   ├── config.py            # Configuration settings
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   └── product.py       # Product model
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── users.py         # User routes
│   │   └── products.py      # Product routes
│   ├── schemas/             # Marshmallow schemas for serialization
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── auth.py          # Authentication utilities
│       ├── errors.py        # Error handling
│       └── pagination.py    # Pagination utilities
├── migrations/              # Database migrations
├── tests/                   # Test cases
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_products.py
├── .env.example             # Example environment variables
├── app.py                   # Application entry point
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

## Requirements

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate
- Flask-RESTful
- Flask-Marshmallow
- Flask-Limiter
- Flask-CORS
- pytest (for testing)

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your settings
   ```
4. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
5. Run the application:
   ```
   python app.py
   ```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (invalidate token)

### Users

- `GET /api/users` - List all users (admin only)
- `GET /api/users/<id>` - Get a specific user
- `PUT /api/users/<id>` - Update a user
- `DELETE /api/users/<id>` - Delete a user

### Products

- `GET /api/products` - List all products
- `POST /api/products` - Create a new product
- `GET /api/products/<id>` - Get a specific product
- `PUT /api/products/<id>` - Update a product
- `DELETE /api/products/<id>` - Delete a product

## Testing

Run tests with pytest:

```
pytest
```

## API Documentation

API documentation is available at `/api/docs` when the server is running.

## License

This project is for educational purposes only. Use responsibly and in accordance with all applicable laws and regulations. 