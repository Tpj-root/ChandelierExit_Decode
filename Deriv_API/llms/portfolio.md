# Portfolio

**Auth:** required (scopes: trade)

Receive information about my current portfolio of outstanding options


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`portfolio_request.schema.json`](https://developers.deriv.com/schemas/portfolio_request.schema.json)
- Response schema: [`portfolio_response.schema.json`](https://developers.deriv.com/schemas/portfolio_response.schema.json)

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
  "portfolio": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `portfolio` | integer: [1] | Yes | Must be `1` |
| `contract_type` | array | No | Return only contracts of the specified types |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `contract_type`

Array of `string: ["HIGHER","LOWER","ACCU","ASIAND","ASIANU","CALL","CALLE","DIGITDIFF","DIGITEVEN","DIGITMATCH","DIGITODD","DIGITOVER","DIGITUNDER","EXPIRYMISSE","EXPIRYMISS","EXPIRYRANGE","EXPIRYRANGEE","MULTDOWN","MULTUP","NOTOUCH","ONETOUCH","PUT","PUTE","RANGE","RESETCALL","RESETPUT","RUNHIGH","RUNLOW","TICKHIGH","TICKLOW","UPORDOWN","VANILLALONGCALL","VANILLALONGPUT","TURBOSLONG","TURBOSSHORT"]`.

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `portfolio` | object | No | Current account's open positions. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["portfolio"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `portfolio`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contracts` | array | Yes | List of open positions. |

_Source: [portfolio](https://developers.deriv.com/llms/portfolio.md)._
