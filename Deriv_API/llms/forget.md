# Forget

**Auth:** not required

Immediately cancel the real-time stream of messages with a specific ID.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`forget_request.schema.json`](https://developers.deriv.com/schemas/forget_request.schema.json)
- Response schema: [`forget_response.schema.json`](https://developers.deriv.com/schemas/forget_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "forget": "d1ee7d0d-3ca9-fbb4-720b-5312d487185b"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `forget` | string, pattern ^[\w-]{32,128}$ | Yes | ID of the real-time stream of messages to cancel. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `forget` | integer: [0,1] | No | If set to 1, stream exited and stopped. If set to 0, stream did not exist. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["forget"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

_Source: [forget](https://developers.deriv.com/llms/forget.md)._
