# Platform Transfer

**Auth:** required (scopes: payment)

Transfer between a wallet and a trading platform account owned by the authenticated client. The body is a strict whitelist - fields not listed here are rejected with 400.

**Endpoint:** `POST /wallet/v1/transfers/platforms`

**Status codes:** 200, 400, 401, 403, 429, 500, 503, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`wallet_transfer_platforms_request.schema.json`](https://developers.deriv.com/schemas/wallet_transfer_platforms_request.schema.json)
- Response schema: [`wallet_transfer_platforms_response.schema.json`](https://developers.deriv.com/schemas/wallet_transfer_platforms_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/wallet/v1/transfers/platforms" \
  -H "Authorization: Bearer <oauth_token>" \
  -H "Content-Type: application/json"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `body` | object | Yes | Send wallet_currency, exchange_rate and rate_token together, or none of them. Supplying one without the other two is rejected with 400. |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |
| `Content-Type` | string: ["application/json"] | Yes | Content type |

### `body`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `wallet_id` | string, (uuid) | Yes | Wallet on the wallet side of the transfer. Must belong to the authenticated client. |
| `amount` | string, pattern ^\d+(\.\d+)?$ | Yes | Transfer amount as a decimal string, in currency. Any applicable fee is deducted from this amount. |
| `currency` | string, pattern ^[A-Z0-9_]{1,18}$ | Yes | Currency of the platform account. Must match the account's actual currency. |
| `direction` | string: ["to_wallet","from_wallet"] | Yes | from_wallet debits the wallet to fund the platform account; to_wallet debits the platform account to fund the wallet. |
| `platform_name` | string: ["mt5","ctrader","options","crypto-exchange","tradingview"] | Yes | Trading platform of the account. |
| `platform_account_id` | string | Yes | Login or account identifier on the platform. Must belong to the authenticated client and be a real account, not a demo one. |
| `request_id` | string, (uuid) | Yes | Idempotency key. Reusing a request_id you have already submitted is rejected with DuplicateRequestID. |
| `description` | string | No | Optional free-text note attached to the transfer. |
| `wallet_currency` | string, pattern ^[A-Z0-9_]{1,18}$ | No | The wallet's currency. Send only for cross-currency platform transfers, when it differs from currency; exchange_rate and rate_token are then required too. |
| `exchange_rate` | string, pattern ^\d+(\.\d+)?$ | No | Quoted exchange rate as a positive decimal string. Required together with rate_token when wallet_currency differs from currency. |
| `rate_token` | string | No | Token attesting to the quoted exchange rate. Required together with exchange_rate when wallet_currency differs from currency. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | Details of the executed platform transfer. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | object | Yes | Status details of the executed transfer. |
| `request_id` | string, (uuid) | Yes | The request_id supplied in the request, echoed back as the idempotency reference of the executed transfer. |

_Source: [wallet-transfer-platforms](https://developers.deriv.com/llms/wallet-transfer-platforms.md)._
