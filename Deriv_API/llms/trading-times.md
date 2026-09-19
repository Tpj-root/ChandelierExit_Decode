# Trading Times

**Auth:** not required

Receive a list of market opening times for a given date.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`trading_times_request.schema.json`](https://developers.deriv.com/schemas/trading_times_request.schema.json)
- Response schema: [`trading_times_response.schema.json`](https://developers.deriv.com/schemas/trading_times_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "trading_times": "2015-09-14"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trading_times` | string, pattern ^([0-9]{4}-[0-9]{1,2}-[0-9]{1,2}\|today)$ | Yes | Date to receive market opening times for. (`yyyy-mm-dd` format. `today` can also be specified). |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trading_times` | object | No | The trading times structure is a hierarchy as follows: Market -> SubMarket -> Underlyings |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["trading_times"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `trading_times`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `markets` | array | Yes | An array of markets |

_Source: [trading-times](https://developers.deriv.com/llms/trading-times.md)._
