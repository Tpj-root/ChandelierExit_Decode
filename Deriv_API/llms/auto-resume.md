# Auto Resume

**Auth:** required (scopes: trade)

Resume a paused automated trading run


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`auto_resume_request.schema.json`](https://developers.deriv.com/schemas/auto_resume_request.schema.json)
- Response schema: [`auto_resume_response.schema.json`](https://developers.deriv.com/schemas/auto_resume_response.schema.json)

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
  "auto_resume": 1,
  "run_id": "atr_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
}));
};
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_resume` | integer: [1] | Yes | Must be `1` |
| `run_id` | string, pattern ^[\w-]{1,128}$ | Yes | The run ID to resume. |
| `passthrough` | object | No | [Optional] Used to pass data through the websocket, which may be retrieved via the `echo_req` output field. |
| `req_id` | integer | No | [Optional] Used to map request to response. |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auto_resume` | object | No | Updated details of the resumed automated trading run |
| `echo_req` | object | Yes | Echo of the request made. |
| `msg_type` | string: ["auto_resume"] | Yes | Action name of the request made. |
| `req_id` | integer | No | Optional field sent in request to map to response, present only when request contains `req_id`. |

### `auto_resume`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_template` | object | Yes | Contract template used for each purchase in this run |
| `contracts` | array | No | List of contracts purchased during this run |
| `run_id` | string | Yes | Unique identifier for the automated trading run |
| `start_time` | integer | Yes | Epoch of when the run was started |
| `status` | string: ["running","paused","stopped"] | Yes | Current status of the run |
| `stop_reason` | string: ["error","user_stopped","condition_triggered"] | No | Reason the run was stopped (absent if still running or paused) |
| `stop_reason_code` | string | No | Code associated with the stop reason (absent if still running or paused) |
| `stop_time` | integer | No | Epoch of when the run was stopped (absent if still running or paused) |
| `strategy_id` | string | Yes | Identifier of the strategy used for this run |
| `strategy_parameters` | object | Yes | Parameters the strategy was started with |
| `total_payout` | number | No | Total amount received from settled contracts in this run |
| `total_stake` | number | No | Total amount spent on contract purchases in this run |

_Source: [auto-resume](https://developers.deriv.com/llms/auto-resume.md)._
