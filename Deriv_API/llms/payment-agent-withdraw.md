# Withdraw

**Auth:** required (scopes: payment)

Withdraw funds from the authenticated client's account through a payment agent

**Endpoint:** `POST /payment-agents/v1/withdraw`

**Status codes:** 200, 400, 401, 403, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`payment_agent_withdraw_request.schema.json`](https://developers.deriv.com/schemas/payment_agent_withdraw_request.schema.json)
- Response schema: [`payment_agent_withdraw_response.schema.json`](https://developers.deriv.com/schemas/payment_agent_withdraw_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/payment-agents/v1/withdraw" \
  -H "Authorization: Bearer <oauth_token>" \
  -H "Content-Type: application/json"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `body` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |
| `Content-Type` | string: ["application/json"] | Yes | Content type |

### `body`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | Withdrawal parameters. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | integer, min 1 | Yes | Unique identifier of the payment agent to withdraw through, as returned by the list endpoint. Values below 1 are rejected with `InvalidAgentID`. |
| `amount` | string, pattern ^(?:0\|[1-9]\d{0,13})(?:\.\d{1,18})?$ | Yes | Amount to withdraw as a decimal string. Must satisfy the agent's `withdrawal_minimum` and `withdrawal_maximum` limits for the currency. |
| `currency` | string, pattern ^[A-Z_]{1,18}$ | Yes | Currency code for the withdrawal. Must be supported by the target payment agent. |
| `verification_code` | string, pattern ^[0-9]{6}$ | Yes | 6-digit one-time verification code obtained from the withdrawal verification code endpoint. |
| `request_id` | string, pattern ^[\w\-]{1,128}$ | No | Optional, 1-128 characters (letters, digits, underscore, hyphen). If provided, the withdrawal status can be retrieved via the withdrawal status endpoint. Without it, status tracking is unavailable for this withdrawal. Must be unique — reusing a previous `request_id` returns `RequestIDUsed`. |
| `notes` | string | No | Optional free-text notes for this transaction. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes |  |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string: ["requested","pending","complete","rejected","failed"] | Yes | Current status of the transaction. Withdrawals start as `pending` and eventually move to `complete`, `rejected`, or `failed`. `requested` is a transient state that callers are unlikely to see. |
| `transaction_id` | integer\|null | Yes | Identifier of the transaction. May be null while the withdrawal is pending. If you supplied a `request_id`, use the withdrawal status endpoint to track its status independently. |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [payment-agent-withdraw](https://developers.deriv.com/llms/payment-agent-withdraw.md)._
