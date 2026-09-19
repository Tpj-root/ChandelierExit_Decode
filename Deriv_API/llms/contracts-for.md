# Contracts For Symbol

**Auth:** not required

For a given symbol, get the list of currently available contracts, and the latest barrier and duration limits for each contract.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`contracts_for_request.schema.json`](https://developers.deriv.com/schemas/contracts_for_request.schema.json)
- Response schema: [`contracts_for_response.schema.json`](https://developers.deriv.com/schemas/contracts_for_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "contracts_for": "R_50"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contracts_for` | string, pattern ^\w{2,30}$ | Yes | The short symbol name (obtained from `active_symbols` call). |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contracts_for` | object | No | List of available contracts. Note: if the user is authenticated, then only contracts allowed under his account will be returned. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["contracts_for"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `contracts_for`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `available` | array, minItems 1 | Yes | Array of available contracts details |
| `hit_count` | number | No | Count of contracts available |

_Source: [contracts-for](https://developers.deriv.com/llms/contracts-for.md)._
