# Update Contract History

**Auth:** required (scopes: trade)

Request for contract update history.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`contract_update_history_request.schema.json`](https://developers.deriv.com/schemas/contract_update_history_request.schema.json)
- Response schema: [`contract_update_history_response.schema.json`](https://developers.deriv.com/schemas/contract_update_history_response.schema.json)

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
  "contract_update_history": 1,
  "contract_id": 123
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_update_history` | integer: [1] | Yes | Must be `1` |
| `contract_id` | integer | Yes | Internal unique contract identifier. |
| `limit` | number, min 1, max 999 | No | [Optional] Maximum number of historical updates to receive. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_update_history` | array | No | Contains the historical and the most recent update status of the contract |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["contract_update_history"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `contract_update_history` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | string | No | Display name of the changed parameter. |
| `order_amount` | string | No | The amount. |
| `order_date` | integer | No | The epoch when the changed was done. |
| `order_type` | string | No | The contract parameter updated. |
| `value` | null\|string | No | The pip-sized barrier value. |

_Source: [contract-update-history](https://developers.deriv.com/llms/contract-update-history.md)._
