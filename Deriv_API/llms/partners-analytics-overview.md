# Partner Analytics Overview

**Auth:** required (scopes: application_read)

Request the authenticated partner's sign-up, master-partner, and activity summaries for an inclusive reporting period.

**Endpoint:** `GET /partners/analytics/v1/overview`

**Status codes:** 200, 400, 401, 403, 404, 422, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`partners_analytics_overview_request.schema.json`](https://developers.deriv.com/schemas/partners_analytics_overview_request.schema.json)
- Response schema: [`partners_analytics_overview_response.schema.json`](https://developers.deriv.com/schemas/partners_analytics_overview_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/partners/analytics/v1/overview" \
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
| `start_date` | string, (date), pattern ^\d{4}-\d{2}-\d{2}$ | Yes | Inclusive start of the reporting period. The period may span at most 730 days. |
| `end_date` | string, (date), pattern ^\d{4}-\d{2}-\d{2}$ | Yes | Inclusive end of the reporting period. Must fall on or after start_date, and no more than 730 days later. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `period` | object | Yes | The inclusive reporting period the summaries cover. |
| `currency` | string, = "USD" | Yes | Currency of every amount in this response. Always USD. |
| `has_lifetime_referred_client` | boolean | Yes | Whether the partner has referred at least one client over their lifetime, regardless of the reporting period. |
| `signups` | object | Yes | Clients who signed up through the partner during the reporting period. |
| `master_partner` | object | Yes | Sub-partner performance, for a partner who manages other partners. |
| `activity` | object | Yes | Commission and trading activity for the reporting period. |

### `period`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start_date` | string, (date) | Yes | Inclusive start of the reporting period. |
| `end_date` | string, (date) | Yes | Inclusive end of the reporting period. |

### `signups`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `total` | integer, min 0 | Yes | Total sign-ups attributed to the partner. |
| `real_accounts` | integer, min 0 | Yes | Sign-ups that opened a real account. |
| `first_time_depositors` | integer, min 0 | Yes | Sign-ups that made their first deposit. |
| `first_time_traders` | integer, min 0 | Yes | Sign-ups that placed their first trade. |

### `master_partner`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `earnings_occurred` | number, (double) | Yes | Master-partner earnings attributed to the reporting period, in USD. |
| `active_subpartners` | integer, min 0 | Yes | Sub-partners who were active during the reporting period. |

### `activity`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paid` | number, (double) | Yes | Paid partner commission for the reporting period, in USD. |
| `pending` | number, (double) | Yes | Pending partner commission for the reporting period, in USD. |
| `active_traders` | integer, min 0 | Yes | Referred clients who traded during the reporting period. |

_Source: [partners-analytics-overview](https://developers.deriv.com/llms/partners-analytics-overview.md)._
