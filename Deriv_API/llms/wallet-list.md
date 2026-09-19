# List Wallets

**Auth:** required (scopes: payment)

Request to list the wallets belonging to the authenticated client, with balances in each wallet's native currency and an optional currency conversion.

**Endpoint:** `GET /wallet/v1/wallets`

**Status codes:** 200, 400, 401, 403, 404, 500, 503, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`wallet_list_request.schema.json`](https://developers.deriv.com/schemas/wallet_list_request.schema.json)
- Response schema: [`wallet_list_response.schema.json`](https://developers.deriv.com/schemas/wallet_list_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/wallet/v1/wallets" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `query` | object | No |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

### `query`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversion_currency` | string, pattern ^[A-Z]{3}$ | No | 3-letter ISO currency code. When supplied, balance amounts are additionally returned converted to this currency. |
| `start_date_time` | string\|integer | No | ISO 8601 timestamp or epoch seconds. Lower bound of the `balance as of` window. |
| `end_date_time` | string\|integer | No | ISO 8601 timestamp or epoch seconds. Upper bound of the `balance as of` window. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | array | Yes | One entry per wallet owned by the authenticated client. |

### `data` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `wallet_id` | string, (uuid) | Yes | Wallet identifier. |
| `type` | string | Yes | Wallet type. |
| `balances` | object | Yes | Balances keyed by 3-letter ISO currency code. |
| `total_balance` | object | No | Only present when `conversion_currency` is set on the request. Shows the wallet's balances summed and converted into the requested currency. Amounts are approximate because FX rates fluctuate. |

### `total_balance`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `converted_to` | string, pattern ^[A-Z]{3}$ | Yes | Currency the totals were converted into — echoes the request's `conversion_currency`. |
| `approximate_total_balance` | string | Yes | Sum of all currency balances converted into `converted_to`. |
| `approximate_total_input` | string | Yes | Sum of all currency inputs converted into `converted_to`. |
| `approximate_total_output` | string | Yes | Sum of all currency outputs converted into `converted_to`. |

_Source: [wallet-list](https://developers.deriv.com/llms/wallet-list.md)._
