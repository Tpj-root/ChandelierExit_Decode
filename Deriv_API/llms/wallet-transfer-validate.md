# Validate Transfer

**Auth:** required (scopes: payment)

Transfer to validate before executing it. The body is a strict whitelist - fields not listed here are rejected with 400.

**Endpoint:** `POST /wallet/v1/transfers/validate`

**Status codes:** 200, 400, 401, 403, 429, 500, 503, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`wallet_transfer_validate_request.schema.json`](https://developers.deriv.com/schemas/wallet_transfer_validate_request.schema.json)
- Response schema: [`wallet_transfer_validate_response.schema.json`](https://developers.deriv.com/schemas/wallet_transfer_validate_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/wallet/v1/transfers/validate" \
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
| `source_type` | string: ["main","p2p","platform","payment_agent"] | Yes | Type of the source account. |
| `destination_type` | string: ["main","p2p","platform","payment_agent"] | Yes | Type of the destination account. |
| `source_id` | string | Yes | Identifier of the source account: the wallet UUID, or the platform account ID such as MTR5312343 when source_type is platform. |
| `destination_id` | string | Yes | Identifier of the destination account: the wallet UUID, or the platform account ID such as MTR5312343 when destination_type is platform. |
| `amount` | string, pattern ^\d+(\.\d+)?$ | Yes | Transfer amount as a decimal string, zero or greater. |
| `balance` | string, pattern ^\d+(\.\d+)?$ | Yes | Current spendable balance of the source account, in source_currency. Same format as amount. Used to check the account holds enough funds. |
| `source_currency` | string, pattern ^[A-Z0-9_]{1,18}$ | Yes | Currency code of the source account. |
| `destination_currency` | string, pattern ^[A-Z0-9_]{1,18}$ | Yes | Currency code of the destination account. |
| `rate` | string, pattern ^\d+(\.\d+)?$ | No | Exchange rate as a positive decimal string. Required when source_currency and destination_currency differ; omit otherwise. |
| `source_platform_name` | string: ["mt5","ctrader","options","crypto-exchange","tradingview"] | No | Platform name. Send when source_type is platform. |
| `destination_platform_name` | string: ["mt5","ctrader","options","crypto-exchange","tradingview"] | No | Platform name. Send when destination_type is platform. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes |  |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `is_valid` | boolean | Yes | Always true - an invalid transfer produces an error response, not false. |
| `details` | object | Yes | Breakdown of the validated transfer. |

### `details`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transfer` | object | Yes | Classification of the validated transfer. |
| `source` | object | Yes | Source side of the validated transfer. All amounts are decimal strings. |
| `destination` | object | Yes | Destination side of the validated transfer. All amounts are decimal strings. |
| `fee` | object | Yes | Fee that would be charged on the transfer. |

_Source: [wallet-transfer-validate](https://developers.deriv.com/llms/wallet-transfer-validate.md)._
