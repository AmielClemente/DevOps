# Website Crawler CRUD API Documentation

## Overview

The Website Crawler CRUD API provides RESTful endpoints for managing target websites that the web crawler monitors. This API allows you to create, read, update, and delete website entries stored in DynamoDB.

## Base URL

```
https://{api-gateway-id}.execute-api.{region}.amazonaws.com/{stage}
```

## Authentication

Currently, the API is public and does not require authentication. In production environments, consider implementing API keys or IAM-based authentication.

## Endpoints

### 1. List All Websites

**GET** `/websites`

Retrieves all target websites from the database.

#### Response

```json
{
  "websites": [
    {
      "id": "uuid-string",
      "url": "https://example.com",
      "name": "Example Website",
      "description": "A sample website",
      "enabled": true,
      "check_interval": 300,
      "timeout": 30,
      "expected_status": 200,
      "created_at": "2024-01-01T00:00:00.000Z",
      "updated_at": "2024-01-01T00:00:00.000Z"
    }
  ],
  "count": 1
}
```

#### Example Request

```bash
curl -X GET https://your-api-gateway-url/websites
```

---

### 2. Get Specific Website

**GET** `/websites/{id}`

Retrieves a specific website by its ID.

#### Parameters

- `id` (path parameter): The unique identifier of the website

#### Response

```json
{
  "website": {
    "id": "uuid-string",
    "url": "https://example.com",
    "name": "Example Website",
    "description": "A sample website",
    "enabled": true,
    "check_interval": 300,
    "timeout": 30,
    "expected_status": 200,
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z"
  }
}
```

#### Example Request

```bash
curl -X GET https://your-api-gateway-url/websites/uuid-string
```

---

### 3. Create New Website

**POST** `/websites`

Creates a new target website entry.

#### Request Body

```json
{
  "url": "https://example.com",
  "name": "Example Website",
  "description": "A sample website",
  "enabled": true,
  "check_interval": 300,
  "timeout": 30,
  "expected_status": 200
}
```

#### Required Fields

- `url`: The website URL to monitor

#### Optional Fields

- `name`: Display name for the website (defaults to URL if not provided)
- `description`: Description of the website
- `enabled`: Whether the website is enabled for monitoring (default: true)
- `check_interval`: Check interval in seconds (default: 300)
- `timeout`: Request timeout in seconds (default: 30)
- `expected_status`: Expected HTTP status code (default: 200)

#### Response

```json
{
  "message": "Website created successfully",
  "website": {
    "id": "generated-uuid",
    "url": "https://example.com",
    "name": "Example Website",
    "description": "A sample website",
    "enabled": true,
    "check_interval": 300,
    "timeout": 30,
    "expected_status": 200,
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T00:00:00.000Z"
  }
}
```

#### Example Request

```bash
curl -X POST https://your-api-gateway-url/websites \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "name": "Example Website",
    "description": "A sample website",
    "enabled": true
  }'
```

---

### 4. Update Website

**PUT** `/websites/{id}`

Updates an existing website entry.

#### Parameters

- `id` (path parameter): The unique identifier of the website

#### Request Body

```json
{
  "name": "Updated Website Name",
  "description": "Updated description",
  "enabled": false,
  "check_interval": 600,
  "timeout": 45,
  "expected_status": 200
}
```

#### Updatable Fields

- `url`: The website URL
- `name`: Display name for the website
- `description`: Description of the website
- `enabled`: Whether the website is enabled for monitoring
- `check_interval`: Check interval in seconds
- `timeout`: Request timeout in seconds
- `expected_status`: Expected HTTP status code

#### Response

```json
{
  "message": "Website updated successfully",
  "website": {
    "id": "uuid-string",
    "url": "https://example.com",
    "name": "Updated Website Name",
    "description": "Updated description",
    "enabled": false,
    "check_interval": 600,
    "timeout": 45,
    "expected_status": 200,
    "created_at": "2024-01-01T00:00:00.000Z",
    "updated_at": "2024-01-01T12:00:00.000Z"
  }
}
```

#### Example Request

```bash
curl -X PUT https://your-api-gateway-url/websites/uuid-string \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Website Name",
    "enabled": false
  }'
```

---

### 5. Delete Website

**DELETE** `/websites/{id}`

Deletes a website entry from the database.

#### Parameters

- `id` (path parameter): The unique identifier of the website

#### Response

```json
{
  "message": "Website deleted successfully"
}
```

#### Example Request

```bash
curl -X DELETE https://your-api-gateway-url/websites/uuid-string
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "URL is required"
}
```

### 404 Not Found

```json
{
  "error": "Website not found"
}
```

### 405 Method Not Allowed

```json
{
  "error": "Method PATCH not allowed"
}
```

### 500 Internal Server Error

```json
{
  "error": "DynamoDB error: ..."
}
```

---

## Data Model

### Website Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | Yes | Unique identifier (UUID) |
| `url` | String | Yes | Website URL to monitor |
| `name` | String | No | Display name (defaults to URL) |
| `description` | String | No | Description of the website |
| `enabled` | Boolean | No | Whether monitoring is enabled (default: true) |
| `check_interval` | Number | No | Check interval in seconds (default: 300) |
| `timeout` | Number | No | Request timeout in seconds (default: 30) |
| `expected_status` | Number | No | Expected HTTP status code (default: 200) |
| `created_at` | String | Yes | ISO timestamp of creation |
| `updated_at` | String | Yes | ISO timestamp of last update |

---

## Rate Limits

Currently, there are no rate limits implemented. In production environments, consider implementing rate limiting to prevent abuse.

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS) and allows requests from any origin. The following headers are supported:

- `Content-Type`
- `X-Amz-Date`
- `Authorization`
- `X-Api-Key`

---

## Performance Considerations

### DynamoDB Performance

- **Read Performance**: Single item reads typically complete within 100ms
- **Write Performance**: Single item writes typically complete within 200ms
- **Scan Performance**: Full table scans may take longer depending on table size

### Best Practices

1. **Use specific IDs**: When possible, use GET `/websites/{id}` instead of scanning all websites
2. **Batch Operations**: For multiple operations, consider implementing batch endpoints
3. **Pagination**: For large datasets, implement pagination in the list endpoint
4. **Caching**: Consider implementing caching for frequently accessed data

---

## Integration with Web Crawler

The CRUD API integrates with the web crawler system as follows:

1. **Configuration Source**: The web crawler reads target websites from the DynamoDB table
2. **Dynamic Updates**: Changes made through the API are automatically reflected in crawler behavior
3. **Monitoring Control**: The `enabled` field allows you to temporarily disable monitoring for specific websites
4. **Customization**: The `check_interval`, `timeout`, and `expected_status` fields allow fine-tuning of monitoring behavior

---

## Example Workflows

### Adding a New Website to Monitor

1. **Create the website entry**:
   ```bash
   curl -X POST https://your-api-gateway-url/websites \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://my-website.com",
       "name": "My Website",
       "description": "My personal website",
       "check_interval": 300
     }'
   ```

2. **Verify the website was created**:
   ```bash
   curl -X GET https://your-api-gateway-url/websites
   ```

3. **The web crawler will automatically start monitoring the new website**

### Temporarily Disabling Website Monitoring

1. **Update the website to disable monitoring**:
   ```bash
   curl -X PUT https://your-api-gateway-url/websites/{website-id} \
     -H "Content-Type: application/json" \
     -d '{"enabled": false}'
   ```

2. **Re-enable monitoring when ready**:
   ```bash
   curl -X PUT https://your-api-gateway-url/websites/{website-id} \
     -H "Content-Type: application/json" \
     -d '{"enabled": true}'
   ```

### Removing a Website from Monitoring

1. **Delete the website entry**:
   ```bash
   curl -X DELETE https://your-api-gateway-url/websites/{website-id}
   ```

2. **The web crawler will stop monitoring the website**

---

## Support

For issues or questions regarding the API:

1. Check the error responses for specific error messages
2. Verify that required fields are provided
3. Ensure the website ID exists for update/delete operations
4. Check DynamoDB table permissions and configuration

---

## Version History

- **v1.0.0**: Initial release with basic CRUD operations
  - Create, Read, Update, Delete website entries
  - DynamoDB integration
  - API Gateway REST endpoints
  - Comprehensive error handling
