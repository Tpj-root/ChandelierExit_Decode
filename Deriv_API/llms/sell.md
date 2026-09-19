# Sell Contract

**Auth:** required (scopes: trade)

Sell a Contract as identified by the `contract_id`.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`sell_request.schema.json`](https://developers.deriv.com/schemas/sell_request.schema.json)
- Response schema: [`sell_response.schema.json`](https://developers.deriv.com/schemas/sell_response.schema.json)

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
  "sell": 11542203588,
  "price": 500
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sell` | integer | Yes | Pass contract_id received from the `portfolio` call. |
| `price` | number | Yes | Minimum price at which to sell the contract, or `0` for 'sell at market'. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sell` | object | No | Receipt for the transaction |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["sell"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `sell`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `balance_after` | number | No | New account balance after completion of the sale |
| `contract_id` | integer | No | Internal contract identifier for the sold contract |
| `reference_id` | integer | No | Internal transaction identifier for the corresponding buy transaction |
| `sold_for` | number | No | Actual effected sale price |
| `transaction_id` | integer | No | Internal transaction identifier for the sale transaction |

_Source: [sell](https://developers.deriv.com/llms/sell.md)._
