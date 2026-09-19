# Auto Start

**Auth:** required (scopes: trade)

Start an automated trading run following a predefined strategy


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`auto_start_request.schema.json`](https://developers.deriv.com/schemas/auto_start_request.schema.json)
- Response schema: [`auto_start_response.schema.json`](https://developers.deriv.com/schemas/auto_start_response.schema.json)

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
  "auto_start": 1,
  "contract_template": {
    "amount": 10,
    "basis": "stake",
    "contract_type": "CALL",
    "currency": "USD",
    "duration": 1,
    "duration_unit": "m",
    "underlying_symbol": "R_100"
  },
  "strategy_id": "martingale",
  "strategy_parameters": {
    "max_stake": 40,
    "multiplier": 2,
    "stop_loss": 50,
    "take_profit": 100
  }
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_start` | integer: [1] | Yes | Must be `1` |
| `contract_template` | object | Yes | Template defining the contract parameters to be used for each purchase in this run |
| `strategy_id` | string, pattern ^\w{1,64}$ | Yes | Identifier of the strategy to run |
| `strategy_parameters` | object | Yes | Parameters specific to the selected strategy (e.g. martingale multiplier, max rounds) |
| `subscribe` | integer: [1] | No | [Optional] If set to `1`, will stream run updates (new contracts purchased, status changes) until the run ends or `forget` is called. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

### `contract_template`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | number, min 0 | No | [Optional] Initial stake or payout value |
| `barrier` | string, pattern ^(?=.{1,20}$)[+-]?[0-9]+\.?[0-9]*$ | No | [Optional] Barrier for the contract (or last digit prediction for digit contracts) |
| `barrier2` | string, pattern ^(?=.{1,20}$)[+-]?[0-9]+\.?[0-9]*$ | No | [Optional] Low barrier for the contract (for contracts with two barriers) |
| `basis` | string: ["payout","stake"] | No | [Optional] Indicates whether amount is 'payout' or 'stake' for binary options |
| `contract_type` | string: ["HIGHER","LOWER","ACCU","ASIAND","ASIANU","CALL","CALLE","DIGITDIFF","DIGITEVEN","DIGITMATCH","DIGITODD","DIGITOVER","DIGITUNDER","EXPIRYMISS","EXPIRYMISSE","EXPIRYRANGE","EXPIRYRANGEE","MULTDOWN","MULTUP","NOTOUCH","ONETOUCH","PUT","PUTE","RANGE","RESETCALL","RESETPUT","RUNHIGH","RUNLOW","TICKHIGH","TICKLOW","TURBOSLONG","TURBOSSHORT","UPORDOWN","VANILLALONGCALL","VANILLALONGPUT"] | Yes | A valid contract type |
| `currency` | string, pattern ^[a-zA-Z0-9]{2,20}$ | Yes | The account-holder's currency |
| `duration` | integer, min 0, max 99999999 | No | [Optional] Duration quantity |
| `duration_unit` | string: ["d","m","s","h","t"] | No | [Optional] Duration unit: `s` seconds, `m` minutes, `h` hours, `d` days, `t` ticks |
| `growth_rate` | number | No | [Optional] Growth rate of an accumulator contract |
| `limit_order` | object | No | [Optional] Order to close the contract once the order condition is met (only for `MULTUP`, `MULTDOWN`, and `ACCU` contracts) |
| `multiplier` | number, min 0 | No | [Optional] The multiplier for non-binary options |
| `selected_tick` | integer | No | [Optional] The tick predicted to have the highest/lowest value - for tickhigh and ticklow contracts |
| `underlying_symbol` | string, pattern ^\w{2,30}$ | Yes | Symbol code |

### `limit_order`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_loss` | number | No | Contract will be automatically closed when the value reaches a specific loss |
| `take_profit` | number | No | Contract will be automatically closed when the value reaches a specific profit |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_start` | object | No | Confirmation of the started automated trading run |
| `subscription` | object | No | For subscription requests only. |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["auto_start"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `auto_start`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_template` | object | Yes | Contract template used for each purchase in this run |
| `contracts` | array | No | List of contracts purchased during this run |
| `run_id` | string | Yes | Unique identifier for the automated trading run |
| `start_time` | integer | Yes | Epoch of when the run was started |
| `status` | string: ["running","paused","stopped"] | Yes | Current status of the run |
| `stop_reason` | string: ["error","user_stopped","condition_triggered"] | No | Reason the run was stopped |
| `stop_reason_code` | string | No | Code associated with the stop reason (absent if still running or paused) |
| `stop_time` | integer | No | Epoch of when the run was stopped |
| `strategy_id` | string | Yes | Identifier of the strategy used for this run |
| `strategy_parameters` | object | Yes | Parameters the strategy was started with |
| `total_payout` | number | No | Total amount received from settled contracts in this run |
| `total_stake` | number | No | Total amount spent on contract purchases in this run |

### `subscription`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | A per-connection unique identifier. Can be passed to the `forget` API call to unsubscribe. |

_Source: [auto-start](https://developers.deriv.com/llms/auto-start.md)._
