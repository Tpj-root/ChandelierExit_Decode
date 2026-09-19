# Auto List

**Auth:** required (scopes: trade)

Retrieve the list of automated trading runs for the current account


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`auto_list_request.schema.json`](https://developers.deriv.com/schemas/auto_list_request.schema.json)
- Response schema: [`auto_list_response.schema.json`](https://developers.deriv.com/schemas/auto_list_response.schema.json)

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
  "auto_list": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_list` | integer: [1] | Yes | Must be `1` |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_list` | object | No | List of automated trading runs |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["auto_list"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `auto_list`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `runs` | array | Yes | Array of automated trading runs |

_Source: [auto-list](https://developers.deriv.com/llms/auto-list.md)._
