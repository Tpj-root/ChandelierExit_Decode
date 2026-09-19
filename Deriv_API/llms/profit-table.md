# Profit Table

**Auth:** required (scopes: trade)

Retrieve a summary of account Profit Table, according to given search criteria


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`profit_table_request.schema.json`](https://developers.deriv.com/schemas/profit_table_request.schema.json)
- Response schema: [`profit_table_response.schema.json`](https://developers.deriv.com/schemas/profit_table_response.schema.json)

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
  "profit_table": 1,
  "description": 1,
  "limit": 25,
  "offset": 25,
  "sort": "ASC"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profit_table` | integer: [1] | Yes | Must be `1` |
| `contract_type` | array | No | Return only contracts of the specified types |
| `date_from` | string, pattern ^([0-9]{4}-(0?[1-9]\|1[012])-(0?[1-9]\|[12][0-9]\|3[01])\|[0-9]{1,10})$ | No | [Optional] Start date (epoch or YYYY-MM-DD) |
| `date_to` | string, pattern ^([0-9]{4}-(0?[1-9]\|1[012])-(0?[1-9]\|[12][0-9]\|3[01])\|[0-9]{1,10})$ | No | [Optional] End date (epoch or YYYY-MM-DD) |
| `description` | integer: [0,1] | No | [Optional] If set to 1, will return full contracts description. |
| `limit` | number, min 0, max 500 | No | [Optional] Apply upper limit to count of transactions received. |
| `offset` | integer, min 0 | No | [Optional] Number of transactions to skip. |
| `sort` | string: ["ASC","DESC"] | No | [Optional] Sort direction. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `contract_type`

Array of `string: ["HIGHER","LOWER","ACCU","ASIAND","ASIANU","CALL","CALLE","DIGITDIFF","DIGITEVEN","DIGITMATCH","DIGITODD","DIGITOVER","DIGITUNDER","EXPIRYMISSE","EXPIRYMISS","EXPIRYRANGE","EXPIRYRANGEE","MULTDOWN","MULTUP","NOTOUCH","ONETOUCH","PUT","PUTE","RANGE","RESETCALL","RESETPUT","RUNHIGH","RUNLOW","TICKHIGH","TICKLOW","UPORDOWN","VANILLALONGCALL","VANILLALONGPUT","TURBOSLONG","TURBOSSHORT"]`.

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profit_table` | object | No | Account Profit Table. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["profit_table"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `profit_table`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `count` | number | No | Number of transactions returned in this call |
| `transactions` | array | No | Array of returned transactions |

_Source: [profit-table](https://developers.deriv.com/llms/profit-table.md)._
