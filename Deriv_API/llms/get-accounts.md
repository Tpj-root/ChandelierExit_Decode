# Get Accounts

**Auth:** required (scopes: trade)

Request to get all Options trading accounts

**Endpoint:** `GET /trading/v1/options/accounts`

**Status codes:** 200, 400, 401, 403, 404, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`get_accounts_request.schema.json`](https://developers.deriv.com/schemas/get_accounts_request.schema.json)
- Response schema: [`get_accounts_response.schema.json`](https://developers.deriv.com/schemas/get_accounts_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/trading/v1/options/accounts" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | array | No |  |
| `meta` | object | No |  |

### `data` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | string | Yes | Account ID |
| `balance` | number | Yes | Account balance |
| `currency` | string | Yes | Account currency |
| `group` | string | Yes | Account group |
| `status` | string: ["active","inactive"] | Yes | Account status |
| `account_type` | string: ["demo","real"] | Yes | Account type |

### `meta`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The current endpoint |
| `method` | string: ["GET","POST","PUT","DELETE"] | Yes | The current HTTP request method |
| `timing` | integer | Yes | Time for the API to serve the request |

_Source: [get-accounts](https://developers.deriv.com/llms/get-accounts.md)._
