# Wallet Transactions

**Auth:** required (scopes: payment)

Request a cursor-paginated list of transactions for one of the authenticated client's wallets, identified by wallet_type.

**Endpoint:** `GET /wallet/v1/transactions/{wallet_type}`

**Status codes:** 200, 400, 401, 403, 404, 500, 503, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`wallet_transactions_request.schema.json`](https://developers.deriv.com/schemas/wallet_transactions_request.schema.json)
- Response schema: [`wallet_transactions_response.schema.json`](https://developers.deriv.com/schemas/wallet_transactions_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/wallet/v1/transactions/{wallet_type}" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `path` | object | Yes |  |
| `query` | object | No |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

### `path`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `wallet_type` | string: ["main","p2p","partner","payment_agent"] | Yes | Wallet type to return transactions for. Resolved server-side against the caller's client identity. |

### `query`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string | No | Filter by the transaction's `request_id`. |
| `transaction_currency` | string, pattern ^[A-Z]{3}$ | No | 3-letter ISO currency code. Restricts the response to transactions in this currency. |
| `start_date_time` | string\|integer | No | ISO 8601 timestamp or epoch seconds. Lower bound of the transaction window. |
| `end_date_time` | string\|integer | No | ISO 8601 timestamp or epoch seconds. Upper bound of the transaction window. |
| `per_page` | integer, min 100, max 1000 | No | Page size. Between 100 and 1000. Defaults to 100. |
| `page_cursor` | string | No | Opaque cursor returned in `links.next` / `links.prev`. When present, other filters are ignored — the cursor encodes them. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | Envelope for the transactions list plus the resolved date range for the current page. |
| `links` | object | Yes | Cursor-based pagination links. Each link contains only `page_cursor` — follow it verbatim to fetch the next / previous page. `null` when the corresponding page does not exist (e.g. `next` on the last page). |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start_date_time` | string\|null, (date-time) | Yes | Lower bound of the returned range. `null` when unbounded. |
| `end_date_time` | string\|null, (date-time) | Yes | Upper bound of the returned range. `null` when unbounded. |
| `transactions` | array | Yes | Transactions on this page, newest first. |

### `links`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `self` | string\|null | Yes | URL of the current page. |
| `next` | string\|null | Yes | URL of the next page, or `null` when there is no next page. |
| `prev` | string\|null | Yes | URL of the previous page, or `null` when there is no previous page. |
| `first` | string\|null | Yes | URL of the first page. |

_Source: [wallet-transactions](https://developers.deriv.com/llms/wallet-transactions.md)._
