# Withdrawal Verification Code

**Auth:** required (scopes: payment)

Request a one-time verification code to be sent to the client's registered contact before submitting a withdrawal

**Endpoint:** `POST /payment-agents/v1/withdraw/verification_code`

**Status codes:** 200, 400, 401, 403, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`payment_agent_withdraw_verification_request.schema.json`](https://developers.deriv.com/schemas/payment_agent_withdraw_verification_request.schema.json)
- Response schema: [`payment_agent_withdraw_verification_response.schema.json`](https://developers.deriv.com/schemas/payment_agent_withdraw_verification_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/payment-agents/v1/withdraw/verification_code" \
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
| `data` | object | Yes | Verification code request parameters. Must match the intended withdrawal. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | integer, min 1 | Yes | Unique identifier of the payment agent to withdraw through, as returned by `GET /payment-agents/v1/agents`. Values below 1 are rejected with `InvalidAgentID`. |
| `amount` | string, pattern ^(?:0\|[1-9]\d{0,13})(?:\.\d{1,18})?$ | Yes | Intended withdrawal amount as a decimal string. |
| `currency` | string, pattern ^[A-Z_]{1,18}$ | Yes | Currency code for the intended withdrawal. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes |  |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | Confirmation message indicating where to look for the code. |
| `next_request_at` | integer | Yes | Epoch timestamp (seconds) before which a new verification code cannot be requested. |
| `expires_at` | integer | Yes | Epoch timestamp (seconds) after which the verification code is no longer valid. |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [payment-agent-withdraw-verification](https://developers.deriv.com/llms/payment-agent-withdraw-verification.md)._
