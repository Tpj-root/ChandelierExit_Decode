# Ticks Stream

**Auth:** not required

Initiate a continuous stream of spot price updates for a given symbol.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`ticks_request.schema.json`](https://developers.deriv.com/schemas/ticks_request.schema.json)
- Response schema: [`ticks_response.schema.json`](https://developers.deriv.com/schemas/ticks_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "ticks": "R_50",
  "subscribe": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticks` |  | Yes | The short symbol name or array of symbols (obtained from `active_symbols` call). |
| `subscribe` | integer: [1] | No | [Optional] If set to 1, will send updates whenever a new tick is received. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `ticks` (one of)

**variant**



**variant**

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tick` | object | No | Tick by tick list of streamed data |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["tick"] | Yes | Type of the response. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `tick`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ask` | number | No | Market ask at the epoch |
| `bid` | number | No | Market bid at the epoch |
| `epoch` | integer | No | Epoch time of the tick |
| `id` | string | No | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |
| `pip_size` | number | Yes | Indicates the number of decimal points that the returned amounts must be displayed with |
| `quote` | number | No | Market value at the epoch |
| `symbol` | string | No | Symbol |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [ticks](https://developers.deriv.com/llms/ticks.md)._
