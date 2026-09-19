# Bulk Purchase

**Auth:** required (Deriv-App-ID + per-account PAT; never Bearer)

Request to buy the same options contract across multiple end-user accounts in a single call

**Endpoint:** `POST /trading/v1/options/contracts/bulk-purchase/{real,demo}`

Each PAT must carry the `trade` scope and own the paired account (max 100 accounts). Invalid entries fail per-account without affecting the others; if none are valid the request is rejected with `400`. `/real` accepts real accounts only and `/demo` accepts demo only — wrong account type is reported as a per-account failure.

**Status codes:** 200, 400, 401, 502


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`bulk_purchase_request.schema.json`](https://developers.deriv.com/schemas/bulk_purchase_request.schema.json)
- Response schema: [`bulk_purchase_response.schema.json`](https://developers.deriv.com/schemas/bulk_purchase_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/trading/v1/options/contracts/bulk-purchase/real" \
  -H "Deriv-App-ID: <app_id>" \
  -H "Content-Type: application/json" \
  -d '{"contract_parameters":{"amount":10,"basis":"stake","contract_type":"CALL","currency":"USD","underlying_symbol":"R_100","duration":5,"duration_unit":"m"},"accounts":[{"account_id":"<account_id>","token":"<PAT>"}]}'
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `body` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier used for Personal Access Token (PAT) authentication. No OAuth access token is required for this endpoint — each account is authorized by its own PAT in the request body. |
| `Content-Type` | string: ["application/json"] | Yes | Content type |

### `body`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_parameters` | object | Yes | Opaque options contract parameters applied to every account in the request (e.g. contract_type, symbol, amount, duration). Passed through unmodified to the trading backend, which validates the contents. |
| `accounts` | array, minItems 1, maxItems 100 | Yes | List of end-user token / account pairs to buy the contract for. Duplicate pairs are honoured and result in repeated purchases. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes |  |
| `meta` | object | Yes |  |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transactions` | array | Yes | Per-account purchase results. Each entry reports success (contract/transaction details) or an error for that account. |

### `meta`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The current endpoint |
| `method` | string: ["GET","POST","PUT","DELETE"] | Yes | The current HTTP request method |
| `timing` | integer | Yes | Time for the API to serve the request |

_Source: [bulk-purchase](https://developers.deriv.com/llms/bulk-purchase.md)._
