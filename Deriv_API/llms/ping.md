# Ping

**Auth:** not required

To send the ping request to the server. Mostly used to test the connection or to keep it alive.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`ping_request.schema.json`](https://developers.deriv.com/schemas/ping_request.schema.json)
- Response schema: [`ping_response.schema.json`](https://developers.deriv.com/schemas/ping_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "ping": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ping` | integer: [1] | Yes | Must be `1` |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ping` | string: ["pong"] | No | Will return 'pong' |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["ping"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

_Source: [ping](https://developers.deriv.com/llms/ping.md)._
