# Check Client Tags

**Auth:** required (scopes: application_read)

Check whether the supplied client IDs are tagged directly to the authenticated partner.

**Endpoint:** `POST /partners/client-tags/check`

**Status codes:** 200, 400, 401, 403, 404, 422, 500, 502, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`partners_client_tags_check_request.schema.json`](https://developers.deriv.com/schemas/partners_client_tags_check_request.schema.json)
- Response schema: [`partners_client_tags_check_response.schema.json`](https://developers.deriv.com/schemas/partners_client_tags_check_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/partners/client-tags/check" \
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
| `client_ids` | array, minItems 1, maxItems 100 | Yes | Client IDs to check. Numeric, UUID, and alphanumeric external ID values are supported. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `partner_id` | integer | Yes | Resolved partner member ID. |
| `total_checked` | integer, min 0 | Yes | Number of client IDs checked. |
| `tagged_count` | integer, min 0 | Yes | Number of checked clients tagged to the partner. |
| `clients` | array | Yes | One result per client ID checked. |

### `clients` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_id` | string | Yes | Sanitised client ID from the request. |
| `is_tagged` | boolean | Yes | Whether the client is tagged directly to the authenticated partner. |

_Source: [partners-client-tags-check](https://developers.deriv.com/llms/partners-client-tags-check.md)._
