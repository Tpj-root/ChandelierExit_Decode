# Active Symbols

**Auth:** not required

Retrieve a list of all currently active symbols (underlying markets upon which contracts are available for trading).


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`active_symbols_request.schema.json`](https://developers.deriv.com/schemas/active_symbols_request.schema.json)
- Response schema: [`active_symbols_response.schema.json`](https://developers.deriv.com/schemas/active_symbols_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "active_symbols": "brief"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `active_symbols` | string: ["full","brief"] | Yes | If you use `brief`, only a subset of fields will be returned. |
| `contract_type` | array | No | [Optional] The proposed contract type |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `contract_type`

Array of `string: ["HIGHER","LOWER","MULTUP","MULTDOWN","UPORDOWN","EXPIRYRANGE","ONETOUCH","CALLE","ASIAND","EXPIRYRANGEE","DIGITDIFF","DIGITMATCH","DIGITOVER","PUTE","DIGITUNDER","NOTOUCH","CALL","RANGE","DIGITODD","PUT","ASIANU","EXPIRYMISSE","EXPIRYMISS","DIGITEVEN","TICKHIGH","TICKLOW","RESETCALL","RESETPUT","RUNHIGH","RUNLOW","ACCU","VANILLALONGCALL","VANILLALONGPUT","TURBOSLONG","TURBOSSHORT"]`.

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `active_symbols` | array | No | List of active symbols. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["active_symbols"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `active_symbols` (array of objects)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exchange_is_open` | integer: [0,1] | Yes | `1` if market is currently open, `0` if closed. |
| `is_trading_suspended` | integer: [0,1] | Yes | `1` indicates that trading is currently suspended, `0` if not. |
| `market` | string | Yes | Market category (forex, indices, etc). |
| `pip_size` | number | Yes | Pip size (i.e. minimum fluctuation amount). |
| `subgroup` | string | Yes | Subgroup name. |
| `submarket` | string | Yes | Submarket name. |
| `trade_count` | integer | Yes | Trade count. |
| `underlying_symbol` | string | Yes | The symbol code for this underlying. |
| `underlying_symbol_name` | string | Yes | Symbol display name. |
| `underlying_symbol_type` | string | Yes | Symbol type (forex, commodities, etc). |

_Source: [active-symbols](https://developers.deriv.com/llms/active-symbols.md)._
