# Contracts List

**Auth:** not required

Get the list of all contract categories available for the trading platform.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`contracts_list_request.schema.json`](https://developers.deriv.com/schemas/contracts_list_request.schema.json)
- Response schema: [`contracts_list_response.schema.json`](https://developers.deriv.com/schemas/contracts_list_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "contracts_list": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contracts_list` | integer: [1] | Yes | Must be 1 |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contracts_list` | array, minItems 1 | No | List of all available contract categories for the trading platform. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["contracts_list"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `contracts_list` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_category` | string | Yes | Internal code for the contract category. |
| `contract_types` | array, minItems 1 | Yes | List of contract type codes belonging to this category. |
| `display_name` | string | Yes | Human-readable name of the contract category. |

_Source: [contracts-list](https://developers.deriv.com/llms/contracts-list.md)._
