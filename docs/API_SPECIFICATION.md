# 📚 Accounts API - Complete Specification

## 📋 Overview

The Accounts API provides a RESTful interface for managing financial accounts. This API follows REST principles with proper HTTP methods, status codes, and resource-oriented design.

**Base URL:** `http://localhost:8000`
**API Version:** 1.0.0
**OpenAPI Spec:** Available at `/openapi.json`
**Interactive Docs:** Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

## 🎯 Design Principles

### RESTful Improvements Made

**Original Implementation Issues:**
- ❌ Used PUT for creating resources (non-standard)
- ❌ Required client to provide account IDs
- ❌ Inconsistent error handling
- ❌ Missing collection endpoints
- ❌ No partial update capability

**Current Implementation:**
- ✅ POST for creating resources (server assigns IDs)
- ✅ Proper HTTP methods for each operation
- ✅ Consistent error responses with proper status codes
- ✅ Complete CRUD operations including collection listing
- ✅ PATCH for partial updates

### Client-Centric Design

The API is designed from a client perspective with these considerations:

1. **Predictable Resource URLs:**
   - `/accounts` - Collection operations
   - `/accounts/{id}` - Individual account operations

2. **Intuitive HTTP Methods:**
   - `GET` for retrieval (safe, idempotent)
   - `POST` for creation (non-idempotent)
   - `PUT` for full updates (idempotent)
   - `PATCH` for partial updates
   - `DELETE` for removal (idempotent)

3. **Consistent Response Format:**
   - Structured JSON responses
   - Consistent error format
   - Clear field validation messages

## 🔗 API Endpoints

### Health Check

#### `GET /health`
**Purpose:** Service health check (Kubernetes-ready)

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-02T17:30:00.000Z",
  "service": "accounts-api",
  "version": "1.0.0"
}
```

---

### Account Management

#### `POST /accounts`
**Purpose:** Create a new account

**Request Body:**
```json
{
  "name": "string (1-100 chars, required)",
  "description": "string (max 500 chars, optional)",
  "balance": "number (≥0, required)",
  "active": "boolean (optional, default: true)"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "John's Savings",
  "description": "Personal savings account",
  "balance": 1000.0,
  "active": true,
  "created_at": "2025-06-02T17:30:00.000Z",
  "updated_at": "2025-06-02T17:30:00.000Z"
}
```

**Errors:**
- `422` - Validation error (invalid data)

---

#### `GET /accounts`
**Purpose:** List all accounts

**Query Parameters:**
- `active_only` (boolean, optional): Filter to show only active accounts

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "John's Savings",
    "description": "Personal savings account",
    "balance": 1000.0,
    "active": true,
    "created_at": "2025-06-02T17:30:00.000Z",
    "updated_at": "2025-06-02T17:30:00.000Z"
  }
]
```

---

#### `GET /accounts/{account_id}`
**Purpose:** Get a specific account by ID

**Path Parameters:**
- `account_id` (integer, required): Account ID

**Response (200):**
```json
{
  "id": 1,
  "name": "John's Savings",
  "description": "Personal savings account",
  "balance": 1000.0,
  "active": true,
  "created_at": "2025-06-02T17:30:00.000Z",
  "updated_at": "2025-06-02T17:30:00.000Z"
}
```

**Errors:**
- `404` - Account not found

---

#### `PUT /accounts/{account_id}`
**Purpose:** Update an existing account (full replacement)

**Path Parameters:**
- `account_id` (integer, required): Account ID

**Request Body:**
```json
{
  "name": "string (1-100 chars, required)",
  "description": "string (max 500 chars, optional)",
  "balance": "number (≥0, required)",
  "active": "boolean (required)"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Updated Account Name",
  "description": "Updated description",
  "balance": 2000.0,
  "active": false,
  "created_at": "2025-06-02T17:30:00.000Z",
  "updated_at": "2025-06-02T17:35:00.000Z"
}
```

**Errors:**
- `404` - Account not found
- `422` - Validation error

---

#### `PATCH /accounts/{account_id}`
**Purpose:** Partially update an existing account

**Path Parameters:**
- `account_id` (integer, required): Account ID

**Request Body (all fields optional):**
```json
{
  "name": "string (1-100 chars, optional)",
  "description": "string (max 500 chars, optional)",
  "balance": "number (≥0, optional)",
  "active": "boolean (optional)"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Partially Updated Name",
  "description": "Original description",
  "balance": 1000.0,
  "active": true,
  "created_at": "2025-06-02T17:30:00.000Z",
  "updated_at": "2025-06-02T17:35:00.000Z"
}
```

**Errors:**
- `404` - Account not found
- `422` - Validation error

---

#### `DELETE /accounts/{account_id}`
**Purpose:** Delete an account

**Path Parameters:**
- `account_id` (integer, required): Account ID

**Response (204):** No content

**Errors:**
- `404` - Account not found

## 📊 Data Models

### Account
```json
{
  "name": "string (1-100 characters)",
  "description": "string (max 500 characters, nullable)",
  "balance": "number (non-negative)",
  "active": "boolean (default: true)"
}
```

### AccountResponse
```json
{
  "id": "integer (server-assigned)",
  "name": "string",
  "description": "string | null",
  "balance": "number",
  "active": "boolean",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)"
}
```

### AccountUpdate (Partial)
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "balance": "number (optional)",
  "active": "boolean (optional)"
}
```

## ⚠️ Error Responses

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "balance"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### Not Found (404)
```json
{
  "detail": "Account with id 999 not found"
}
```

### Internal Server Error (500)
```json
{
  "detail": "Internal server error while creating account"
}
```

## 🔍 Client Usage Examples

### Creating an Account
```bash
curl -X POST "http://localhost:8000/accounts" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My Savings",
       "description": "Personal savings account",
       "balance": 1500.0,
       "active": true
     }'
```

### Listing Active Accounts Only
```bash
curl "http://localhost:8000/accounts?active_only=true"
```

### Partial Update
```bash
curl -X PATCH "http://localhost:8000/accounts/1" \
     -H "Content-Type: application/json" \
     -d '{"balance": 2000.0}'
```

## 🎯 Minimum Viable Client Interface

The API provides the minimum essential operations a client needs:

1. **Create Account** - Basic account setup
2. **Read Account** - View account details
3. **List Accounts** - Browse all accounts with filtering
4. **Update Account** - Both full and partial updates
5. **Delete Account** - Account removal
6. **Health Check** - Service monitoring

This covers the complete CRUD lifecycle that any account management client would require.

## 🔄 REST Compliance

✅ **Resource-based URLs:** `/accounts` and `/accounts/{id}`
✅ **HTTP methods align with operations:** GET (read), POST (create), PUT (update), PATCH (partial), DELETE (remove)
✅ **Stateless:** No server-side session state
✅ **Consistent response format:** JSON with predictable structure
✅ **Proper status codes:** 200, 201, 204, 404, 422, 500
✅ **Idempotent operations:** GET, PUT, DELETE behave consistently
✅ **Collection and resource endpoints:** Both supported appropriately
