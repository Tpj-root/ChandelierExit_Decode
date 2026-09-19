# Cancel a Contract

**Auth:** required (scopes: trade)

Cancel contract with contract id


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`cancel_request.schema.json`](https://developers.deriv.com/schemas/cancel_request.schema.json)
- Response schema: [`cancel_response.schema.json`](https://developers.deriv.com/schemas/cancel_response.schema.json)

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
  "cancel": 11542203588
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cancel` | integer | Yes | Value should be the `contract_id` which received from the `portfolio` call. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cancel` | object | No | Receipt for the transaction |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["cancel"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `cancel`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `balance_after` | number | No | New account balance after completion of the sale |
| `contract_id` | integer | No | Internal contract identifier for the sold contract |
| `reference_id` | integer | No | Internal transaction identifier for the corresponding buy transaction |
| `sold_for` | number | No | Actual effected sale price |
| `transaction_id` | integer | No | Internal transaction identifier for the sale transaction |

_Source: [cancel](https://developers.deriv.com/llms/cancel.md)._
