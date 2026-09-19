# Buy Contract

**Auth:** required (scopes: trade)

Buy a Contract


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`buy_request.schema.json`](https://developers.deriv.com/schemas/buy_request.schema.json)
- Response schema: [`buy_response.schema.json`](https://developers.deriv.com/schemas/buy_response.schema.json)

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
  "buy": "uw2mk7no3oktoRVVsB4Dz7TQnFfABuFDgO95dlxfMxRuPUsz",
  "price": 100
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `buy` | string, pattern ^(?:[\w-]{32,128}\|1)$ | Yes | Either the ID received from a Price Proposal (`proposal` call), or `1` if contract buy parameters are passed in the `parameters` field. |
| `parameters` | object | No | [Optional] Used to pass the parameters for contract buy. |
| `price` | number, min 0 | Yes | Maximum price at which to purchase the contract. |
| `subscribe` | integer: [1] | No | [Optional] `1` to stream. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `parameters`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | number, min 0 | No | [Optional] Proposed payout or stake value |
| `app_markup_percentage` | number | No | [Optional] Markup added to contract prices (as a percentage of contract payout) |
| `barrier` | string, pattern ^(?=.{1,20}$)[+-]?[0-9]+\.?[0-9]*$ | No | [Optional] Barrier for the contract (or last digit prediction for digit contracts). Contracts less than 24 hours in duration would need a relative barrier (barriers which need +/-), where entry spot would be adjusted accordingly with that amount to define a barrier, except for Synthetic Indices as they support both relative and absolute barriers. |
| `barrier2` | string, pattern ^(?=.{1,20}$)[+-]?[0-9]+\.?[0-9]*$ | No | [Optional] Low barrier for the contract (for contracts with two barriers). Contracts less than 24 hours in duration would need a relative barrier (barriers which need +/-), where entry spot would be adjusted accordingly with that amount to define a barrier, except for Synthetic Indices as they support both relative and absolute barriers. |
| `basis` | string: ["payout","stake"] | No | [Optional] Indicates whether amount is 'payout' or 'stake' for binary options. |
| `cancellation` | string, pattern ^\w+$ | No | Cancellation duration option (only for `MULTUP` and `MULTDOWN` contracts). |
| `contract_type` | string: ["HIGHER","LOWER","ACCU","ASIAND","ASIANU","CALL","CALLE","DIGITDIFF","DIGITEVEN","DIGITMATCH","DIGITODD","DIGITOVER","DIGITUNDER","EXPIRYMISS","EXPIRYMISSE","EXPIRYRANGE","EXPIRYRANGEE","MULTDOWN","MULTUP","NOTOUCH","ONETOUCH","PUT","PUTE","RANGE","RESETCALL","RESETPUT","RUNHIGH","RUNLOW","TICKHIGH","TICKLOW","TURBOSLONG","TURBOSSHORT","UPORDOWN","VANILLALONGCALL","VANILLALONGPUT"] | Yes | A valid contract-type |
| `currency` | string, pattern ^[a-zA-Z0-9]{2,20}$ | Yes | This can only be the account-holder's currency |
| `date_expiry` | integer, min 1, max 9999999999 | No | [Optional] Epoch value of the expiry time of the contract. You must either specify date_expiry or duration. |
| `duration` | integer, min 0, max 99999999 | No | [Optional] Duration quantity |
| `duration_unit` | string: ["d","m","s","h","t"] | No | [Optional] Duration unit is `s`: seconds, `m`: minutes, `h`: hours, `d`: days, `t`: ticks |
| `growth_rate` | number | No | [Optional] Growth rate of an accumulator contract. |
| `limit_order` | object | No | Add an order to close the contract once the order condition is met (only for `MULTUP` and `MULTDOWN` and `ACCU` contracts). |
| `multiplier` | number, min 0 | No | [Optional] The multiplier for non-binary options. E.g. lookbacks. |
| `payout_per_point` | number | No | [Optional] Clients can provide payout_per_point directly, and the barrier will be calculated based on this payout_per_point value. |
| `selected_tick` | integer | No | [Optional] The tick that is predicted to have the highest/lowest value - for tickhigh and ticklow contracts. |
| `underlying_symbol` | string, pattern ^\w{2,30}$ | Yes | Symbol code |

### `limit_order`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_loss` | number | No | Contract will be automatically closed when the value of the contract reaches a specific loss. |
| `take_profit` | number | No | Contract will be automatically closed when the value of the contract reaches a specific profit. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `buy` | object | No | Receipt confirmation for the purchase |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["buy"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `buy`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `balance_after` | number | Yes | The new account balance after completion of the purchase |
| `buy_price` | number | Yes | Actual effected purchase price |
| `contract_id` | integer | Yes | Internal contract identifier |
| `longcode` | string | Yes | The description of contract purchased |
| `payout` | number | Yes | Proposed payout value |
| `purchase_time` | integer | Yes | Epoch value of the transaction purchase time |
| `shortcode` | string | Yes | Compact description of the contract purchased |
| `start_time` | integer | Yes | Epoch value showing the expected start time of the contract |
| `transaction_id` | integer | Yes | Internal transaction identifier |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [buy](https://developers.deriv.com/llms/buy.md)._
