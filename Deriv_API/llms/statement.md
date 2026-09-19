# Statement

**Auth:** required (scopes: trade)

Retrieve a summary of account transactions, according to given search criteria


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`statement_request.schema.json`](https://developers.deriv.com/schemas/statement_request.schema.json)
- Response schema: [`statement_response.schema.json`](https://developers.deriv.com/schemas/statement_response.schema.json)

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
  "statement": 1,
  "description": 1,
  "limit": 100,
  "offset": 25
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `statement` | integer: [1] | Yes | Must be `1` |
| `action_type` | string: ["buy","sell","deposit","withdrawal"] | No | [Optional] To filter the statement according to the type of transaction. |
| `date_from` | integer, min 0, max 9999999999 | No | [Optional] Start date (epoch) |
| `date_to` | integer, min 0, max 9999999999 | No | [Optional] End date (epoch) |
| `description` | integer: [0,1] | No | [Optional] If set to 1, will return full contracts description. |
| `limit` | number, min 0, max 999 | No | [Optional] Maximum number of transactions to receive. |
| `offset` | integer, min 0 | No | [Optional] Number of transactions to skip. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `statement` | object | No | Account statement. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["statement"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `statement`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `count` | number | No | Number of transactions returned in this call |
| `transactions` | array | No | Array of returned transactions |

_Source: [statement](https://developers.deriv.com/llms/statement.md)._
