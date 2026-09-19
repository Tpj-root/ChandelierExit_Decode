# Balance

**Auth:** required (scopes: trade)

Get the account's balance


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`balance_request.schema.json`](https://developers.deriv.com/schemas/balance_request.schema.json)
- Response schema: [`balance_response.schema.json`](https://developers.deriv.com/schemas/balance_response.schema.json)

## Example

```bash
curl -X POST "https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
# => { "data": { "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..." } }
```

```javascript
const ws = new WebSocket(otpUrl); // wss://api.derivws.com/trading/v1/options/ws/real?otp=...
ws.onopen = () => {
  ws.send(JSON.stringify({
  "balance": 1,
  "subscribe": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `balance` | integer: [1] | Yes | Must be `1` |
| `subscribe` | integer: [0,1] | No | [Optional] If set to 1, will send updates whenever the balance changes. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `balance` | object | No | Current balance of one or more accounts. |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["balance"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `balance`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `balance` | number, min 0 | Yes | Balance of current account. |
| `currency` | string, pattern ^(\|[a-zA-Z0-9]{2,20})$ | Yes | Currency of current account. |
| `id` | string | No | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |
| `loginid` | string, pattern ^[A-Z]{2,4}[0-9]{1,10}$ | Yes | Client loginid. |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [balance](https://developers.deriv.com/llms/balance.md)._
