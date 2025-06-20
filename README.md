# Furniture Product Management API

A complete, production-ready FastAPI backend system for product management with admin functionality and Excel import capabilities.

## Features

- **Product Management**: Complete CRUD operations for products
- **Admin Authentication**: JWT-based authentication system
- **Excel Import**: Bulk product import from Excel files
- **Search & Filtering**: Advanced product search and filtering
- **Auto Documentation**: Swagger UI and ReDoc integration
- **Database Migrations**: Alembic for database versioning
- **Production Ready**: Comprehensive error handling and logging

## Technology Stack

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM with database abstraction
- **Alembic** - Database migrations
- **PostgreSQL/SQLite** - Database systems
- **JWT** - Authentication tokens
- **Pydantic** - Data validation
- **openpyxl/pandas** - Excel processing

## Project Structure

```
furniture-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   └── admin.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   └── admin.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       └── products.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_processor.py
│   │   └── product_service.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── alembic/
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd furniture-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your actual configuration values
```

### 5. Database Setup

```bash
# Initialize Alembic
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Public Endpoints

- `GET /api/v1/products/` - List all active products
- `GET /api/v1/products/{id}` - Get product details
- `GET /api/v1/products/categories` - Get all categories
- `GET /api/v1/products/search` - Search products

### Admin Endpoints (Authentication Required)

- `POST /api/v1/admin/login` - Admin login
- `POST /api/v1/admin/upload-excel` - Upload Excel file
- `GET /api/v1/admin/products/` - Get all products
- `PUT /api/v1/admin/products/{id}` - Update product
- `DELETE /api/v1/admin/products/{id}` - Delete product
- `GET /api/v1/admin/upload-history` - Upload history

## Excel Import Format

The Excel file should have the following columns:

| Column | Field | Type | Required |
|--------|-------|------|----------|
| A | Product Name | String | Yes |
| B | Description | Text | No |
| C | Price | Decimal | Yes |
| D | Category | String | No |
| E | Brand | String | No |
| F | SKU | String | No |
| G | Stock Quantity | Integer | No |
| H | Image URL | String | No |
| I | Tags | String (comma-separated) | No |

## Authentication

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/admin/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
```

### Using JWT Token
```bash
curl -X GET "http://localhost:8000/api/v1/admin/products/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Configuration

### SQLite (Development)
```env
DATABASE_URL=sqlite:///./furniture.db
```

### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://user:password@localhost/furniture_db
POSTGRES_USER=furniture_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=furniture_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Production Deployment

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

Make sure to set these in production:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@host/db
DEBUG=false
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Type Checking

```bash
mypy app/
```

## API Examples

### Get Products with Filtering

```bash
curl "http://localhost:8000/api/v1/products/?category=Electronics&min_price=100&max_price=1000&page=1&size=10"
```

### Search Products

```bash
curl "http://localhost:8000/api/v1/products/search?q=laptop&category=Electronics"
```

### Upload Excel File

```bash
curl -X POST "http://localhost:8000/api/v1/admin/upload-excel" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@products.xlsx"
```

## Error Handling

The API returns consistent error responses:

```json
{
    "error": "validation_error",
    "message": "Product validation failed",
    "details": [
        {"field": "price", "message": "Price must be positive"},
        {"field": "name", "message": "Product name is required"}
    ],
    "timestamp": "2024-01-01T10:00:00Z"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
