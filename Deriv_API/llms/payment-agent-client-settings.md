# Client Settings

**Auth:** required (scopes: payment)

Request the authenticated client's current payment agent settings

**Endpoint:** `GET /payment-agents/v1/clients/me`

**Status codes:** 200, 401, 403, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`payment_agent_client_settings_request.schema.json`](https://developers.deriv.com/schemas/payment_agent_client_settings_request.schema.json)
- Response schema: [`payment_agent_client_settings_response.schema.json`](https://developers.deriv.com/schemas/payment_agent_client_settings_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/payment-agents/v1/clients/me" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | The client's current settings for using payment agents. |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deposit_enabled` | boolean | Yes | Whether the client can currently receive deposits from payment agents (that is, be the recipient of a transfer). |
| `withdraw_enabled` | boolean | Yes | Whether the client can currently withdraw funds through a payment agent. |
| `show_real_name` | boolean | Yes | Whether payment agents see the client's real name on transactions. `false` withholds the real name. |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [payment-agent-client-settings](https://developers.deriv.com/llms/payment-agent-client-settings.md)._
