# Transfer Between Wallets

**Auth:** required (scopes: payment)

Same-currency transfer between two wallets owned by the authenticated client. The body is a strict whitelist - fields not listed here are rejected with 400.

**Endpoint:** `POST /wallet/v1/transfers`

**Status codes:** 200, 400, 401, 403, 429, 500, 503, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`wallet_transfer_request.schema.json`](https://developers.deriv.com/schemas/wallet_transfer_request.schema.json)
- Response schema: [`wallet_transfer_response.schema.json`](https://developers.deriv.com/schemas/wallet_transfer_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/wallet/v1/transfers" \
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
| `currency` | string, pattern ^[A-Z0-9_]{1,18}$ | Yes | Currency of the transfer. Both wallets must hold a balance in this currency. |
| `amount` | string, pattern ^\d+(\.\d+)?$ | Yes | Transfer amount as a decimal string. Any applicable fee is deducted from this amount. |
| `source_wallet_id` | string, (uuid) | Yes | Wallet to debit. Must belong to the authenticated client. |
| `destination_wallet_id` | string, (uuid) | Yes | Wallet to credit. Must belong to the authenticated client. |
| `request_id` | string, (uuid) | Yes | Idempotency key. Reusing a request_id you have already submitted does not create a duplicate transfer. |
| `description` | string | No | Optional free-text note attached to the transfer. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | Details of the executed transfer. Always echoes the request's request_id; the remaining fields describe the recorded transfer. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string, (uuid) | Yes | The request_id supplied in the request, echoed back as the idempotency reference of the executed transfer. |

_Source: [wallet-transfer](https://developers.deriv.com/llms/wallet-transfer.md)._
