# BuryatVPN API Documentation

## Authentication

All admin API endpoints require JWT authentication.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

## Endpoints

### Health Check

```http
GET /health
```

Returns system health status.

### Metrics

```http
GET /metrics
```

Returns Prometheus metrics.

### Users

#### Get Users List

```http
GET /api/v1/users
Authorization: Bearer <token>
```

#### Get User Profile

```http
GET /api/v1/users/{telegram_id}
Authorization: Bearer <token>
```

#### Ban User

```http
POST /api/v1/users/{telegram_id}/ban
Authorization: Bearer <token>
Content-Type: application/json

{
  "banned": true
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Rate Limiting

- Default: 1000 requests per hour, 100 per minute
- Admin endpoints: 500 requests per hour
- Authentication: 10 requests per minute
