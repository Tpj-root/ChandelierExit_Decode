# Exchange Rate

**Auth:** required (scopes: payment)

Request a quote for converting between two currencies.

**Endpoint:** `GET /wallet/v1/exchange-rate`

**Status codes:** 200, 400, 401, 403, 429, 500, 503, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`wallet_exchange_rate_request.schema.json`](https://developers.deriv.com/schemas/wallet_exchange_rate_request.schema.json)
- Response schema: [`wallet_exchange_rate_response.schema.json`](https://developers.deriv.com/schemas/wallet_exchange_rate_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/wallet/v1/exchange-rate" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `query` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

### `query`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_currency` | string, pattern ^[A-Z0-9_]{1,18}$ | Yes | Currency to convert from. |
| `destination_currency` | string, pattern ^[A-Z0-9_]{1,18}$ | Yes | Currency to convert to. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | The quote for the requested currency pair. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exchange_rate` | string | No | Quoted exchange rate as a decimal string. |
| `rate_token` | string | No | Token attesting to this quote. Pass it, together with the rate, to POST /wallet/v1/transfers/exchange or to a cross-currency POST /wallet/v1/transfers/platforms request to execute at the quoted rate. |

_Source: [wallet-exchange-rate](https://developers.deriv.com/llms/wallet-exchange-rate.md)._
