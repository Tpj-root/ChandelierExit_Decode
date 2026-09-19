# Forget All

**Auth:** not required

Immediately cancel the real-time streams of messages of given type.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`forget_all_request.schema.json`](https://developers.deriv.com/schemas/forget_all_request.schema.json)
- Response schema: [`forget_all_response.schema.json`](https://developers.deriv.com/schemas/forget_all_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "forget_all": "ticks"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `forget_all` |  | Yes | Cancel all streams by type. The value can be either a single type e.g. `"ticks"`, or an array of multiple types e.g. `["candles", "ticks"]`. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `forget_all` (one of)

**variant**



**variant**

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `forget_all` | array | No | IDs of the cancelled streams |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["forget_all"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `forget_all`

Array of `items`.

_Source: [forget-all](https://developers.deriv.com/llms/forget-all.md)._
