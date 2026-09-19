# Get Payment Agent

**Auth:** required (scopes: payment)

Request for the full profile of a single payment agent

**Endpoint:** `GET /payment-agents/v1/agents/{id}`

**Status codes:** 200, 400, 401, 403, 404, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`payment_agent_get_request.schema.json`](https://developers.deriv.com/schemas/payment_agent_get_request.schema.json)
- Response schema: [`payment_agent_get_response.schema.json`](https://developers.deriv.com/schemas/payment_agent_get_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/payment-agents/v1/agents/{id}" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |
| `path` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

### `path`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Numeric ID of the payment agent (as returned by the list endpoint) or the literal string `me` to return the authenticated client's own agent profile. Any other non-numeric value returns `InvalidAgentID`. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes |  |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique identifier of the payment agent. |
| `cashier_withdraw` | boolean | No | Whether the agent is allowed to withdraw from the payment agent wallet (only returned when viewing own profile). |
| `transfer_to_pa` | boolean | No | Whether the agent is permitted to transfer funds to other payment agents (only returned when viewing own profile). |
| `created_at` | integer | No | Epoch timestamp (milliseconds) when the agent was registered. |
| `is_listed` | boolean | No | Whether the agent appears in the public agent directory. |
| `name` | string\|null | No | Display name of the payment agent. |
| `nickname` | string\|null | No | Short display handle for the payment agent. |
| `information` | string\|null | No | Free-text description of the agent's services and operating details. |
| `email` | string\|null | No | Contact email address. |
| `phone_numbers` | array\|null | No | Contact phone numbers. |
| `payment_methods` | array\|null | No | Payment methods accepted by this agent. |
| `countries` | array\|null | No | ISO 3166-1 alpha-2 country codes in lowercase in which this agent operates. |
| `urls` | array\|null | Yes | Website URLs associated with the agent. May be null when the agent has no registered URLs. |
| `currencies` | array | Yes | Commission and limit settings for each currency the agent supports. |
| `deposit_enabled` | boolean | No | Whether the agent is allowed to perform deposits to their own wallet (only returned when viewing own profile). |
| `withdraw_enabled` | boolean | No | Whether the agent is allowed to perform withdrawals from their own wallet (only returned when viewing own profile). |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [payment-agent-get](https://developers.deriv.com/llms/payment-agent-get.md)._
