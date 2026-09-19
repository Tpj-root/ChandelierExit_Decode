# Ticks History

**Auth:** not required

Get historic tick data for a given symbol.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`ticks_history_request.schema.json`](https://developers.deriv.com/schemas/ticks_history_request.schema.json)
- Response schema: [`ticks_history_response.schema.json`](https://developers.deriv.com/schemas/ticks_history_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "ticks_history": "R_50",
  "adjust_start_time": 1,
  "count": 10,
  "end": "latest",
  "start": 1,
  "style": "ticks"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticks_history` | string, pattern ^\w{2,30}$ | Yes | Short symbol name (obtained from the `active_symbols` call). |
| `adjust_start_time` | integer: [1] | No | [Optional] 1 - if the market is closed at the end time, or license limit is before end time, adjust interval backwards to compensate. |
| `count` | integer | No | [Optional] An upper limit on ticks to receive. |
| `end` | string, pattern ^(latest\|[0-9]{1,10})$ | Yes | Epoch value representing the latest boundary of the returned ticks. If `latest` is specified, this will be the latest available timestamp. |
| `granularity` | integer: [60,120,180,300,600,900,1800,3600,7200,14400,28800,86400] | No | [Optional] Only applicable for style: `candles`. Candle time-dimension width setting. (default: `60`). |
| `start` | integer, min 0, max 9999999999 | No | [Optional] Epoch value representing the earliest boundary of the returned ticks.  - For `"style": "ticks"`: this will default to 1 day ago. - For `"style": "candles"`: it will default to 1 day ago if count or granularity is undefined. |
| `style` | string: ["candles","ticks"] | No | [Optional] The tick-output style. |
| `subscribe` | integer: [1] | No | [Optional] 1 - to send updates whenever a new tick is received. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `candles` | array | No | Array of OHLC (open/high/low/close) price values for the given time (only for style=`candles`) |
| `history` | object | No | Historic tick data for a given symbol. Note: this will always return the latest possible set of ticks with accordance to the parameters specified. |
| `pip_size` | number | No | Indicates the number of decimal points that the returned amounts must be displayed with |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["history","tick","candles","ohlc"] | Yes | Type of the response according to the `style` sent in request. Would be `history` or `candles` for the first response, and `tick` or `ohlc` for the rest when subscribed. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `candles` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `close` | number | No | It is the close price value for the given time |
| `epoch` | integer | No | It is an epoch value |
| `high` | number | No | It is the high price value for the given time |
| `low` | number | No | It is the low price value for the given time |
| `open` | number | No | It is the open price value for the given time |

### `history`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prices` | array | No | An array containing list of tick values for the corresponding epoch values in `times` array. |
| `times` | array | No | An array containing list of epoch values for the corresponding tick values in `prices` array. |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [ticks-history](https://developers.deriv.com/llms/ticks-history.md)._
