# Update Contract

**Auth:** required (scopes: trade)

Update a contract condition.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`contract_update_request.schema.json`](https://developers.deriv.com/schemas/contract_update_request.schema.json)
- Response schema: [`contract_update_response.schema.json`](https://developers.deriv.com/schemas/contract_update_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
# => { "data": { "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..." } }
```

```javascript
const ws = new WebSocket(otpUrl); // wss://api.derivws.com/trading/v1/options/ws/real?otp=...
ws.onopen = () => {
  ws.send(JSON.stringify({
  "contract_update": 1,
  "contract_id": 123,
  "limit_order": {
    "take_profit": 1
  }
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_update` | integer: [1] | Yes | Must be `1` |
| `contract_id` | integer | Yes | Internal unique contract identifier. |
| `limit_order` | object | Yes | Specify limit order to update. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `limit_order`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_loss` | null\|number | No | New stop loss value for a contract. To cancel, pass `null`. |
| `take_profit` | null\|number | No | New take profit value for a contract. To cancel, pass `null`. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_update` | object | No | Contains the update status of the request |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["contract_update"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `contract_update`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_loss` | object | No | The target spot price where the contract will be closed automatically at the loss specified by the user. |
| `take_profit` | object | No | The target spot price where the contract will be closed automatically at the profit specified by the user. |

### `stop_loss`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | string | No | Localized display name |
| `order_amount` | null\|number | No | Stop loss amount |
| `order_date` | integer | No | Stop loss order epoch |
| `value` | null\|string | No | Stop loss pip-sized barrier value |

### `take_profit`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | string | No | Localized display name |
| `order_amount` | null\|number | No | Take profit amount |
| `order_date` | integer | No | Take profit order epoch |
| `value` | null\|string | No | Take profit pip-sized barrier value |

_Source: [contract-update](https://developers.deriv.com/llms/contract-update.md)._
