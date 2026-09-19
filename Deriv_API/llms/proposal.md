# Price Proposal

**Auth:** not required

Gets latest price for a specific contract.


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`proposal_request.schema.json`](https://developers.deriv.com/schemas/proposal_request.schema.json)
- Response schema: [`proposal_response.schema.json`](https://developers.deriv.com/schemas/proposal_response.schema.json)

## Example

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => {
  ws.send(JSON.stringify({
  "proposal": 1,
  "amount": 100,
  "barrier": "+0.1",
  "basis": "payout",
  "contract_type": "HIGHER",
  "currency": "USD",
  "duration": 60,
  "duration_unit": "s",
  "underlying_symbol": "R_100"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

```bash
curl -X POST "https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
# => { "data": { "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..." } }
```

```javascript
const ws = new WebSocket(otpUrl); // wss://api.derivws.com/trading/v1/options/ws/real?otp=...
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.msg_type === "proposal") {
    ws.send(JSON.stringify({ "buy": msg.proposal.id, "price": msg.proposal.ask_price }));
  }
};
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `proposal` | integer: [1] | Yes | Must be `1` |
| `amount` | number, min 0 | No | [Optional] Proposed contract payout or stake. |
| `barrier` | string, pattern ^(?=.{1,20}$)[+-]?[0-9]+\.?[0-9]*$ | No | [Optional] Barrier for the contract (or last digit prediction for digit contracts). Contracts less than 24 hours in duration would need a relative barrier (barriers which need +/-), where entry spot would be adjusted accordingly with that amount to define a barrier, except for Synthetic Indices as they support both relative and absolute barriers. Not needed for lookbacks. |
| `barrier2` | string, pattern ^(?=.{1,20}$)[+-]?[0-9]+\.?[0-9]*$ | No | [Optional] Low barrier for the contract (for contracts with two barriers). Contracts less than 24 hours in duration would need a relative barrier (barriers which need +/-), where entry spot would be adjusted accordingly with that amount to define a barrier, except for Synthetic Indices as they support both relative and absolute barriers. Not needed for lookbacks. |
| `basis` | string: ["payout","stake"] | No | [Optional] Indicates type of the `amount`. |
| `cancellation` | string, pattern ^\w+$ | No | Cancellation duration option (only for `MULTUP` and `MULTDOWN` contracts). |
| `contract_type` | string: ["HIGHER","LOWER","MULTUP","MULTDOWN","UPORDOWN","EXPIRYRANGE","ONETOUCH","CALLE","ASIAND","EXPIRYRANGEE","DIGITDIFF","DIGITMATCH","DIGITOVER","PUTE","DIGITUNDER","NOTOUCH","CALL","RANGE","DIGITODD","PUT","ASIANU","EXPIRYMISSE","EXPIRYMISS","DIGITEVEN","TICKHIGH","TICKLOW","RESETCALL","RESETPUT","RUNHIGH","RUNLOW","ACCU","VANILLALONGCALL","VANILLALONGPUT","TURBOSLONG","TURBOSSHORT"] | Yes | The proposed contract type |
| `currency` | string, pattern ^[a-zA-Z0-9]{2,20}$ | Yes | This can only be the account-holder's currency (obtained from `payout_currencies` call). |
| `date_expiry` | integer, min 0, max 9999999999 | No | [Optional] Epoch value of the expiry time of the contract. Either date_expiry or duration is required. |
| `duration` | integer, min 0, max 99999999 | No | [Optional] Duration quantity. Either date_expiry or duration is required. |
| `duration_unit` | string: ["d","m","s","h","t"] | No | [Optional] Duration unit - `s`: seconds, `m`: minutes, `h`: hours, `d`: days, `t`: ticks. |
| `growth_rate` | number | No | [Optional] Growth rate of an accumulator contract. |
| `limit_order` | object | No | Add an order to close the contract once the order condition is met (only for `MULTUP` and `MULTDOWN` and 'ACCU' contracts). Supported orders: `take_profit`, `stop_loss`. |
| `multiplier` | number, min 0 | No | [Optional] The multiplier for non-binary options. E.g. lookbacks. |
| `payout_per_point` | number | No | [Optional] Clients can provide payout_per_point directly, and the barrier will be calculated based on this payout_per_point value. |
| `selected_tick` | integer | No | [Optional] The tick that is predicted to have the highest/lowest value - for `TICKHIGH` and `TICKLOW` contracts. |
| `subscribe` | integer: [1] | No | [Optional] 1 - to initiate a realtime stream of prices. Note that tick trades (without a user-defined barrier), digit trades and less than 24 hours at-the-money contracts for the following underlying symbols are not streamed: `R_10`, `R_25`, `R_50`, `R_75`, `R_100`, `RDBULL`, `RDBEAR` (this is because their price is constant). |
| `underlying_symbol` | string, pattern ^\w{2,30}$ | Yes | The symbol code (obtained from `active_symbols` call). |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `limit_order`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_loss` | number | No | Contract will be automatically closed when the value of the contract reaches a specific loss. |
| `take_profit` | number | No | Contract will be automatically closed when the value of the contract reaches a specific profit. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `proposal` | object | No | Latest price and other details for a given contract |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["proposal"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `proposal`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ask_price` | number | Yes | The ask price. |
| `barrier_choices` | array | No | [Only for vanilla options] The choices of predefined strike price for client to choose |
| `barrier_spot_distance` | string | No | [Only for Turbos] The relative distance between current spot and the barrier. |
| `cancellation` | object | No | Contains information about contract cancellation option. |
| `commission` | null\|number | No | Commission changed in percentage (%). |
| `contract_details` | object | No | Contains contract information. |
| `date_expiry` | integer | No | The end date of the contract. |
| `date_start` | integer | Yes | The start date of the contract. |
| `display_number_of_contracts` | string | No | [Only for vanilla or turbos options] The implied number of contracts |
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |
| `limit_order` | object | No | Contains limit order information. (Only applicable for contract with limit order). |
| `longcode` | string | Yes | Example: Win payout if Random 100 Index is strictly higher than entry spot at 15 minutes after contract start time. |
| `max_stake` | number | No | [Only for vanilla or turbos options] Maximum stakes allowed |
| `min_stake` | number | No | [Only for vanilla or turbos options] Minimum stakes allowed |
| `multiplier` | number | No | [Only for lookback trades] Multiplier applies when calculating the final payoff for each type of lookback. e.g. (Exit spot - Lowest historical price) * multiplier = Payout |
| `payout` | number | Yes | The payout amount of the contract. |
| `payout_choices` | array | No | [Only for Turbos] The choices of predefined payout per point for client to choose |
| `spot` | number | Yes | Spot value (if there are no Exchange data-feed licensing restrictions for the underlying symbol). |
| `spot_time` | integer | Yes | The corresponding time of the spot value. |
| `validation_params` | object | No | Contains contract validation information. |

### `cancellation`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ask_price` | number | No | Ask price of contract cancellation option. |
| `date_expiry` | integer | No | Expiry time in epoch for contract cancellation option. |

### `contract_details`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_markup_amount` | string | No | The markup amount charged on a client's stake amount |
| `barrier` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | Barrier of the contract. |
| `barrier_spot_distance` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | Absolute difference between high/low barrier and spot |
| `high_barrier` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | High barrier calculated based on current spot |
| `last_tick_epoch` | integer | No | Epoch of last tick considered for stat chart |
| `low_barrier` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | Low barrier calculated based on current spot |
| `maximum_payout` | number | No | Maximum payout that user can get out of a contract, contract will close automatically if payout reaches this number |
| `maximum_stake` | string | No | Maximum stake that user can set to buy a contract |
| `maximum_ticks` | integer | No | Maximum duration that a contract can last, contract will close automatically after this number of ticks |
| `minimum_stake` | string | No | Minimum stake that user can set to buy a contract |
| `tick_size_barrier` | number | No | Tick size barrier for Accumulator contracts |
| `tick_size_barrier_percentage` | string | No | [Accumulator] Tick size barrier in percentage, rounded off to 5 decimal places |
| `ticks_stayed_in` | array | No | An array of numbers  to build a stat chart - each number represents the duration that spot stayed between barries |

### `limit_order`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_loss` | object | No | Contains information where the contract will be closed automatically at the loss specified by the user. |
| `stop_out` | object | No | Contains information where the contract will be closed automatically when the value of the contract is close to zero. This is set by the us. |
| `take_profit` | object | No | Contains information where the contract will be closed automatically at the profit specified by the user. |

### `validation_params`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `max_payout` | string | No | [Only for Accumulators] Maximum payout for the contract. |
| `max_ticks` | integer | No | [Only for Accumulators] Maximum ticks for the contract. |
| `payout` | object | No | Contains information for minimum and maximum payout amount for the contract. |
| `stake` | object | No | Contains information for minimum and maximum stake amount for the contract. |
| `stop_loss` | object | No | [Only for Multipliers] Contains information for minimum and maximum stop loss amount for the contract. |
| `take_profit` | object | No | Contains information for minimum and maximum take profit amount for the contract. |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [proposal](https://developers.deriv.com/llms/proposal.md)._
