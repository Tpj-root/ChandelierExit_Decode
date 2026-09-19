# Transfer (Deposit)

**Auth:** required (scopes: payment)

Request for a payment agent to deposit funds into a client's Deriv wallet

**Endpoint:** `POST /payment-agents/v1/transfer`

**Status codes:** 200, 400, 401, 403, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`payment_agent_transfer_request.schema.json`](https://developers.deriv.com/schemas/payment_agent_transfer_request.schema.json)
- Response schema: [`payment_agent_transfer_response.schema.json`](https://developers.deriv.com/schemas/payment_agent_transfer_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/payment-agents/v1/transfer" \
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
| `data` | object | Yes | Transfer parameters. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to_nickname` | string | Yes | Deriv account nickname of the client to receive the funds. |
| `amount` | string, pattern ^(?:0\|[1-9]\d{0,13})(?:\.\d{1,18})?$ | Yes | Amount to transfer expressed as a decimal string. |
| `currency` | string, pattern ^[A-Z_]{1,18}$ | Yes | Currency code for the transfer. Must be supported by the authenticated payment agent. |
| `notes` | string | No | Optional free-text notes for this transaction. |
| `request_id` | string, pattern ^[\w\-]{1,128}$ | No | Optional idempotency key, 1-128 characters (letters, digits, underscore, hyphen). Reusing a previous `request_id` returns `RequestIDUsed` instead of creating a duplicate transfer. If the transfer doesn't complete immediately (`status: "pending"`), use this `request_id` with `GET /payment-agents/v1/transfer/{request_id}` to poll for the final status. |
| `dry_run` | boolean | No | When `true`, the request runs validation and returns success without creating a transaction. Use to preflight a transfer before committing. The response `status` is `dry_run_ok` and `transaction_id` is `null`. A `dry_run` never fails with `RequestIDUsed` — uniqueness is checked only on the real call. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | Result of the transfer call. |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string: ["complete","pending","dry_run_ok"] | Yes | `complete` when a real transfer was executed. `pending` when the transfer was accepted but is still being processed — use `GET /payment-agents/v1/transfer/{request_id}` with the supplied `request_id` to poll for the final status. `dry_run_ok` when `dry_run` was `true` and only validation was performed. |
| `transaction_id` | integer\|null | Yes | Identifier of the created transaction. `null` when `status` is `dry_run_ok` or `pending`. |
| `client_real_name` | string\|null | Yes | Recipient's real name. Returned when the recipient shares it by setting `show_real_name` to `true`. `null` if they keep it private or it cannot be resolved. |
| `client_is_agent` | boolean | Yes | Whether the recipient is itself another payment agent. `true` for transfers between two payment agents, `false` for a transfer to a regular client. |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [payment-agent-transfer](https://developers.deriv.com/llms/payment-agent-transfer.md)._
