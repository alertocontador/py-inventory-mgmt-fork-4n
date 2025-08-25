---
title: "Design and implement few critical APIs for inventory management"
tags:
  - postgresql
summary: "Inventory management is a critical excercise for any online business. In this challenge you will be implementing few core APIs for inventory management"
---

## Problem Statement

You are tasked with implementing critical APIs for an inventory management system. These APIs handle SKU creation, temporary inventory blocking, and block management operations essential for e-commerce platforms.

### API Requirements

Your implementation must provide the following API endpoints:

#### 1. POST /sku
Create a new SKU (Stock Keeping Unit) in the inventory system.

**Sample Request:**
```json
POST /sku
Content-Type: application/json

{
  "sku_code": "ABC123",
  "name": "Wireless Headphones",
  "quantity": 100,
  "price": 99.99
}
```

**Sample Response:**
```json
HTTP 200 OK
Content-Type: application/json

{
  "sku_id": "550e8400-e29b-41d4-a716-446655440000",
  "sku_code": "ABC123",
  "name": "Wireless Headphones",
  "quantity": 100,
  "price": 99.99,
  "created_at": "2023-12-25T10:30:00Z"
}
```

#### 2. POST /sku/{sku_id}/temporary-block
Create a temporary block on inventory to reserve items for a pending transaction.

**Sample Request:**
```json
POST /sku/550e8400-e29b-41d4-a716-446655440000/temporary-block
Content-Type: application/json

{
  "quantity": 5,
  "reason": "Order processing",
  "expires_at": "2023-12-25T12:00:00Z"
}
```

**Sample Response:**
```json
HTTP 200 OK
Content-Type: application/json

{
  "block_id": "660f9500-f39c-52e5-b827-557766551111",
  "sku_id": "550e8400-e29b-41d4-a716-446655440000",
  "quantity": 5,
  "reason": "Order processing",
  "status": "active",
  "expires_at": "2023-12-25T12:00:00Z",
  "created_at": "2023-12-25T10:45:00Z"
}
```

#### 3. GET /temporary-blocks
Retrieve all active temporary blocks in the system.

**Sample Request:**
```
GET /temporary-blocks
```

**Sample Response:**
```json
HTTP 200 OK
Content-Type: application/json

{
  "blocks": [
    {
      "block_id": "660f9500-f39c-52e5-b827-557766551111",
      "sku_id": "550e8400-e29b-41d4-a716-446655440000",
      "sku_code": "ABC123",
      "quantity": 5,
      "reason": "Order processing",
      "status": "active",
      "expires_at": "2023-12-25T12:00:00Z",
      "created_at": "2023-12-25T10:45:00Z"
    }
  ],
  "total": 1
}
```

#### 4. POST /temporary-blocks/{block_id}/convert-to-permanent
Convert a temporary inventory block to a permanent reduction (e.g., when order is confirmed).

**Sample Request:**
```json
POST /temporary-blocks/660f9500-f39c-52e5-b827-557766551111/convert-to-permanent
Content-Type: application/json

{
  "reason": "Order confirmed - SKU ABC123"
}
```

**Sample Response:**
```json
HTTP 200 OK
Content-Type: application/json

{
  "block_id": "660f9500-f39c-52e5-b827-557766551111",
  "status": "converted",
  "converted_at": "2023-12-25T11:30:00Z",
  "reason": "Order confirmed - SKU ABC123"
}
```

#### 5. POST /temporary-blocks/{block_id}/cancel
Cancel a temporary block and return the reserved inventory to available stock.

**Sample Request:**
```json
POST /temporary-blocks/660f9500-f39c-52e5-b827-557766551111/cancel
Content-Type: application/json

{
  "reason": "Order cancelled by customer"
}
```

**Sample Response:**
```json
HTTP 200 OK
Content-Type: application/json

{
  "block_id": "660f9500-f39c-52e5-b827-557766551111",
  "status": "cancelled",
  "cancelled_at": "2023-12-25T11:15:00Z",
  "reason": "Order cancelled by customer"
}
```

## Development Setup

### FastAPI Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.dev .env
   ```

3. **Run Development Server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Database Services

### Database Initialization
If you need to initialize your database schema, you can use the `init.sql` file:
- Edit `init.sql` to add your database schema, tables, and indexes
- Run the SQL file against your database to set up the initial structure

### PostgreSQL
- **Host**: py-inventory-mgmtpostgresql
- **Port**: 5432
- **Database**: postgres
- **User**: postgres
- **Password**: postgres

## Development Workflow

1. Make your changes to the code
2. Test locally using the development server
3. Ensure all tests pass
4. Deploy using the production configuration

## Production Deployment

The application uses `.env.prod` for production environment variables with Kubernetes service names for database connections.