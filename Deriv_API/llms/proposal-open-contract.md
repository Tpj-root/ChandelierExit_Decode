# Price Proposal: Open Contracts

**Auth:** required (scopes: trade)

Get the latest price (and other information) for contract(s) in the account's portfolio


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`proposal_open_contract_request.schema.json`](https://developers.deriv.com/schemas/proposal_open_contract_request.schema.json)
- Response schema: [`proposal_open_contract_response.schema.json`](https://developers.deriv.com/schemas/proposal_open_contract_response.schema.json)

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
  "proposal_open_contract": 1,
  "contract_id": 11111111,
  "subscribe": 1
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `proposal_open_contract` | integer: [1] | Yes | Must be `1` |
| `contract_id` | integer | No | [Optional] Contract ID received from a `portfolio` request. If not set, you will receive stream of all open contracts. |
| `subscribe` | integer: [1] | No | [Optional] `1` to stream. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `proposal_open_contract` | object | No | Latest price and other details for an open contract |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["proposal_open_contract"] | No | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `proposal_open_contract`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | number | No | Account Id |
| `app_markup_amount` | string | No | The markup amount charged on a client's stake amount |
| `audit_details` | null\|object | No | Tick details around contract start and end time. |
| `auto_run_id` | string | No | Identifier of the automated run that purchased this contract. |
| `barrier` | null\|string | No | Barrier of the contract (if any). |
| `barrier_count` | number | No | The number of barriers a contract has. |
| `barrier_spot_distance` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | [Only for accumulator] Absolute difference between high/low barrier and spot |
| `bid_price` | string | No | Price at which the contract could be sold back to the company. |
| `buy_price` | string | No | Price at which contract was purchased |
| `cancellation` | object | No | Contains information about contract cancellation option. |
| `commission` | null\|string | No | Commission in payout currency amount. |
| `contract_id` | integer | No | The internal contract identifier |
| `contract_type` | string | No | Contract type. |
| `currency` | string | No | The currency code of the contract. |
| `current_spot` | string | No | Spot value if we have license to stream this symbol. |
| `current_spot_high_barrier` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | [Applicable for accumulator] High barrier based on current spot. |
| `current_spot_low_barrier` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | [Applicable for accumulator] Low barrier based on current spot. |
| `current_spot_time` | integer | No | The corresponding time of the current spot. |
| `date_expiry` | integer | No | Expiry date (epoch) of the Contract. Please note that it is not applicable for tick trade contracts. |
| `date_settlement` | integer | No | Settlement date (epoch) of the contract. |
| `date_start` | integer | No | Start date (epoch) of the contract. |
| `display_number_of_contracts` | string | No | [Only for vanilla or turbos options] The implied number of contracts |
| `entry_spot` | null\|string | No | The first valid underlying spot price for the contract. |
| `entry_spot_time` | integer\|null | No | This is the epoch time of the entry spot. |
| `exit_spot` | null\|string | No | Exit spot can refer to the latest quote at the end time, the quote that fulfils the contract's winning or losing condition for path dependent contracts (Touch/No Touch and Stays Between/Goes Outside) or the quote at which the contract is sold before expiry. |
| `exit_spot_time` | integer\|null | No | This is the epoch time of the exit spot. Note that since certain instruments don't tick every second, the exit spot time may be a few seconds before the end time. |
| `expiry_time` | integer | No | This is the expiry time. |
| `growth_rate` | number | No | [Only for accumulator] Growth rate of an accumulator contract. |
| `high_barrier` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | High barrier of the contract (if any). |
| `id` | string | No | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |
| `is_expired` | integer: [0,1] | No | Whether the contract is expired or not. |
| `is_intraday` | integer: [0,1] | No | Whether the contract is an intraday contract. |
| `is_path_dependent` | integer: [0,1] | No | Whether the contract expiry price will depend on the path of the market (e.g. One Touch contract). |
| `is_settleable` | integer: [0,1] | No | Whether the contract is settleable or not. |
| `is_sold` | integer: [0,1] | No | Whether the contract is sold or not. |
| `is_valid_to_cancel` | integer: [0,1] | No | Whether the contract can be cancelled. |
| `is_valid_to_sell` | integer: [0,1] | No | Whether the contract can be sold back to the company. |
| `is_valid_to_update` | null\|object | No | [Optional] Indicator whether take profit, stop loss, and/or stop out is allowed to be updated. |
| `limit_order` | object | No | Orders are applicable to `MULTUP` and `MULTDOWN` contracts only. |
| `longcode` | string | No | Text description of the contract purchased, Example: Win payout if Volatility 100 Index is strictly higher than entry spot at 10 minutes after contract start time. |
| `low_barrier` | string, pattern ^[+-]?[0-9]+\.?[0-9]*$ | No | Low barrier of the contract (if any). |
| `multiplier` | number | No | [Only for lookback trades] Multiplier applies when calculating the final payoff for each type of lookback. e.g. (Exit spot - Lowest historical price) * multiplier = Payout |
| `payout` | string | No | Payout value of the contract. |
| `profit` | string | No | The latest bid price minus buy price. |
| `profit_percentage` | number | No | Profit in percentage. |
| `purchase_time` | integer | No | Epoch of purchase time, will be same as `date_start` for all contracts except forward starting contracts. |
| `reset_barrier` | null\|string | No | [Only for reset trades i.e. RESETCALL and RESETPUT] Reset barrier of the contract. |
| `reset_time` | integer | No | [Only for reset trades i.e. RESETCALL and RESETPUT] The epoch time of a barrier reset. |
| `selected_spot` | null\|string | No | Spot value at the selected tick for the contract. |
| `selected_tick` | integer | No | [Only for highlowticks trades i.e. TICKHIGH and TICKLOW] Selected tick for the contract. |
| `sell_price` | null\|string | No | Price at which contract was sold, only available when contract has been sold. |
| `sell_time` | integer\|null | No | Epoch time of when the contract was sold (only present for contracts already sold) |
| `shortcode` | string | No | Coded description of the contract purchased. |
| `status` | null,string: ["open","sold","won","lost","cancelled",null] | No | Contract status. Will be `sold` if the contract was sold back before expiry, `won` if won and `lost` if lost at expiry. Otherwise will be `open` |
| `tick_count` | integer | No | Only for tick trades, number of ticks |
| `tick_passed` | integer | No | [Only for accumulator] Number of ticks passed since entry_tick |
| `tick_stream` | array | No | Tick stream from entry to end time. |
| `transaction_ids` | object | No | Every contract has buy and sell transaction ids, i.e. when you purchase a contract we associate it with buy transaction id, and if contract is already sold we associate that with sell transaction id. |
| `underlying_symbol` | string | No | The underlying symbol code. |
| `validation_error` | string | No | Error message if validation fails |
| `validation_error_code` | string | No | Error code if validation fails |
| `validation_error_code_args` | array\|null | No | Error code arguments if validation fails |
| `validation_params` | object | No | Contains contract validation information. |

### `cancellation`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ask_price` | null\|number | No | Ask price of contract cancellation option. |
| `date_expiry` | integer | No | Expiry time in epoch for contract cancellation option. |

### `limit_order`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_loss` | object | No | Contains information where the contract will be closed automatically at the loss specified by the user. |
| `stop_out` | object | No | Contains information where the contract will be closed automatically when the value of the contract is close to zero. This is set by the us. |
| `take_profit` | object | No | Contain information where the contract will be closed automatically at the profit specified by the user. |

### `transaction_ids`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `buy` | integer | No | Buy transaction ID for that contract |
| `sell` | integer | No | Sell transaction ID for that contract, only present when contract is already sold. |

### `validation_params`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `max_payout` | string | No | [Only for Accumulators] Maximum payout for the contract. |
| `max_ticks` | integer | No | [Only for Accumulators] Maximum ticks for the contract. |
| `stake` | object | No | Contains information for minimum and maximum stake amount for the contract. |
| `stop_loss` | object | No | [Only for Multipliers] Contains information for minimum and maximum stop loss amount for the contract. |
| `take_profit` | object | No | Contains information for minimum and maximum take profit amount for the contract. |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [proposal-open-contract](https://developers.deriv.com/llms/proposal-open-contract.md)._
