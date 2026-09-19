# WebSockets

**Auth:** required (scopes: trade)

Request to obtain an OTP-authenticated WebSocket URL for Options trading

**Endpoint:** `POST /trading/v1/options/accounts/{accountId}/otp`

**Status codes:** 200, 400, 401, 500


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`websocket_request.schema.json`](https://developers.deriv.com/schemas/websocket_request.schema.json)
- Response schema: [`websocket_response.schema.json`](https://developers.deriv.com/schemas/websocket_response.schema.json)

## Example

Call `POST /trading/v1/options/accounts/{accountId}/otp` with `Authorization: Bearer <token>` (plus `Deriv-App-ID` when using PAT auth); the response returns a one-time WebSocket URL — connect to it and send messages.

```bash
curl -X POST "https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

```json
{
  "data": {
    "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..."
  }
}
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `path` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

### `path`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `accountId` | string | Yes | Options Trading account ID that the OTP is requested for |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes |  |
| `meta` | object | Yes |  |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | WebSocket URL with embedded OTP — connect to this URL directly |

### `meta`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The current endpoint |
| `method` | string: ["GET","POST","PUT","DELETE"] | Yes | The current HTTP request method |
| `timing` | integer | Yes | Time for the API to serve the request |

_Source: [websocket](https://developers.deriv.com/llms/websocket.md)._
