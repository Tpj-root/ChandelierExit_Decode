# Withdrawal Status

**Auth:** required (scopes: payment)

Request the current status of a withdrawal previously submitted with a request_id

**Endpoint:** `GET /payment-agents/v1/withdraw/{request_id}`

**Status codes:** 200, 400, 401, 403, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`payment_agent_withdraw_status_request.schema.json`](https://developers.deriv.com/schemas/payment_agent_withdraw_status_request.schema.json)
- Response schema: [`payment_agent_withdraw_status_response.schema.json`](https://developers.deriv.com/schemas/payment_agent_withdraw_status_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/payment-agents/v1/withdraw/{request_id}" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
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
| `request_id` | string, pattern ^[\w\-]{1,128}$ | Yes | The `request_id` previously passed to the withdraw endpoint (1-128 characters: letters, digits, underscore, hyphen). A malformed value returns `InvalidRequestIDFormat`; a well-formed value that doesn't match any of your withdrawals returns `RequestIDNotFound`. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes |  |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string: ["requested","pending","complete","rejected","failed"] | Yes | Current status of the withdrawal. Poll until it reaches `complete`, `rejected`, or `failed`. `requested` is a transient state that callers are unlikely to see. |
| `transaction_id` | integer\|null | Yes | Identifier of the transaction. May be null in some cases regardless of `status`. |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [payment-agent-withdraw-status](https://developers.deriv.com/llms/payment-agent-withdraw-status.md)._
