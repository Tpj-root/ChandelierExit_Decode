# Transactions Stream

**Auth:** required (scopes: trade)

Subscribe to transaction notifications


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`transaction_request.schema.json`](https://developers.deriv.com/schemas/transaction_request.schema.json)
- Response schema: [`transaction_response.schema.json`](https://developers.deriv.com/schemas/transaction_response.schema.json)

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
  "transaction": 1,
  "subscribe": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction` | integer: [1] | Yes | Must be `1` |
| `subscribe` | integer: [1] | Yes | If set to 1, will send updates whenever there is an update to transactions. If not to 1 then it will not return any records. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction` | object | No | Realtime stream of user transaction updates. |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["transaction"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `transaction`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string: ["buy","sell","deposit","withdrawal"] | No | The transaction type. |
| `amount` | number | No | It is the amount of transaction performed. |
| `balance` | number, min 0, max 10000000000000000000 | No | Balance amount |
| `contract_id` | integer\|null | No | It is the contract ID. |
| `currency` | string | No | Transaction currency |
| `date_expiry` | integer | No | Epoch value of the expiry time of the contract. Please note that in case of buy transaction this is approximate value not exact one. |
| `id` | string | No | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |
| `longcode` | string | No | Description of contract purchased |
| `purchase_time` | integer | No | Time at which contract was purchased, present only for sell transaction |
| `transaction_id` | integer | No | It is the transaction ID. Every contract (buy or sell) or payment has a unique ID. |
| `transaction_time` | integer | No | Time at which transaction was performed: for buy it is purchase time, for sell it is sell time. |
| `underlying_symbol` | string | No | Symbol code |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [transaction](https://developers.deriv.com/llms/transaction.md)._
