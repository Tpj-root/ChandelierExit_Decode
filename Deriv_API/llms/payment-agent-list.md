# List Payment Agents

**Auth:** required (scopes: payment)

Request to list active payment agents that support a currency

**Endpoint:** `GET /payment-agents/v1/agents`

**Status codes:** 200, 400, 401, 403, 500, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`payment_agent_list_request.schema.json`](https://developers.deriv.com/schemas/payment_agent_list_request.schema.json)
- Response schema: [`payment_agent_list_response.schema.json`](https://developers.deriv.com/schemas/payment_agent_list_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/payment-agents/v1/agents" \
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
| `currency` | string | Yes | Currency code. Only agents that support this currency are returned. |
| `country` | string | No | ISO 3166-1 alpha-2 country code in lowercase (e.g. `id`). When supplied, only agents whose `countries` list includes this value are returned. |
| `page` | integer | No | Page number for pagination. Defaults to 1. |
| `per_page` | integer | No | Number of results per page. Defaults to 25. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | array | Yes | Payment agent list items sorted by agent ID ascending. |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique identifier of the payment agent. Pass this as `agent_id` to the withdraw endpoint. |
| `created_at` | integer | No | Epoch timestamp (milliseconds) when the agent was registered. |
| `is_listed` | boolean | No | Whether the agent appears in the public agent directory. `false` indicates this agent was included because you've previously received a transfer from them, not because they're publicly listed. |
| `name` | string\|null | No | Display name of the payment agent. |
| `nickname` | string\|null | No | Short display handle for the payment agent. |
| `information` | string\|null | No | Free-text description of the agent's services and operating details. |
| `email` | string\|null | No | Contact email address of the payment agent. |
| `phone_numbers` | array\|null | No | Contact phone numbers. |
| `payment_methods` | array\|null | No | Payment methods accepted by this agent (e.g. `bank_transfer`, `mobile_money`). |
| `countries` | array\|null | No | ISO 3166-1 alpha-2 country codes in lowercase in which this agent operates. |
| `urls` | array\|null | No | Website links for the agent. |
| `deposit_commission` | number\|null | No | Commission rate for deposits in the queried currency. |
| `withdrawal_commission` | number\|null | No | Commission rate for withdrawals in the queried currency. |
| `withdrawal_minimum` | string\|null | No | Minimum withdrawal amount as a decimal string for the queried currency. |
| `withdrawal_maximum` | string\|null | No | Maximum withdrawal amount as a decimal string for the queried currency. |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [payment-agent-list](https://developers.deriv.com/llms/payment-agent-list.md)._
