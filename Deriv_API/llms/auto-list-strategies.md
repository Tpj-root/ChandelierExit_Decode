# Auto List Strategies

**Auth:** not required

Retrieve the list of available automated trading strategies


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`auto_list_strategies_request.schema.json`](https://developers.deriv.com/schemas/auto_list_strategies_request.schema.json)
- Response schema: [`auto_list_strategies_response.schema.json`](https://developers.deriv.com/schemas/auto_list_strategies_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "auto_list_strategies": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_list_strategies` | integer: [1] | Yes | Must be `1` |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_list_strategies` | object | No | List of available automated trading strategies |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["auto_list_strategies"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `auto_list_strategies`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `strategies` | array | Yes | Array of available strategies |

_Source: [auto-list-strategies](https://developers.deriv.com/llms/auto-list-strategies.md)._
