# Markup Statistics

**Auth:** required (scopes: application_read)

Query parameters for the GET /applications/v1/markup-statistics endpoint.

**Endpoint:** `GET /applications/v1/markup-statistics`

**Status codes:** 200, 400, 401, 403, 404, 422, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`markup_statistics_request.schema.json`](https://developers.deriv.com/schemas/markup_statistics_request.schema.json)
- Response schema: [`markup_statistics_response.schema.json`](https://developers.deriv.com/schemas/markup_statistics_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/applications/v1/markup-statistics" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. Passed as a request header. |
| `date_from` | string, (date), pattern ^\d{4}-\d{2}-\d{2}$ | Yes | Interval start date (YYYY-MM-DD), inclusive, UTC. |
| `date_to` | string, (date), pattern ^\d{4}-\d{2}-\d{2}$ | Yes | Interval end date (YYYY-MM-DD), inclusive, UTC. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | Markup and trading aggregates for the caller's applications over the requested date range. Root fields sum across all included apps; `breakdown` lists the same metrics per application. |
| `meta` | object | Yes | Response metadata. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `total_app_markup_usd` | number | Yes | Sum of application markup attributed to all included apps in the interval. |
| `total_volume_usd` | number | Yes | Sum of contract volume (buy price in USD terms) across all included apps in the interval. |
| `total_payout_usd` | number | Yes | Sum of all potential payouts (in USD terms) across all included apps in the interval. |
| `total_contract_count` | integer | Yes | Total number of contracts counted toward the aggregates across all included apps. |
| `total_client_count` | integer | Yes | Number of distinct client accounts that traded under any included app in the interval. |
| `breakdown` | array | Yes | Per-application rows; each entry corresponds to one app_id with metrics for that app only. |

### `meta`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The API endpoint path that was called. |
| `method` | string: ["GET","POST","PUT","DELETE"] | Yes | The HTTP method used. |
| `timing` | integer | Yes | Request processing time in milliseconds. |

_Source: [markup-statistics](https://developers.deriv.com/llms/markup-statistics.md)._
