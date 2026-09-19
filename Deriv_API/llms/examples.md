# Code Examples

Current API only.

## Public market data (no auth)

```javascript
const ws = new WebSocket('wss://api.derivws.com/trading/v1/options/ws/public');
ws.onopen = () => ws.send(JSON.stringify({ "ticks": "R_100", "subscribe": 1 }));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

## Authenticated trading — full propose → buy flow

### Step 1. Get an OTP WebSocket URL (REST)

```bash
curl -X POST https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
# -> { "data": { "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..." } }
```

### Step 2. Connect to the returned URL and propose

```javascript
const ws = new WebSocket(otpUrl); // URL from step 1 — no auth message needed
ws.onopen = () => ws.send(JSON.stringify({
  "proposal": 1,
  "amount": 10,
  "basis": "stake",
  "contract_type": "CALL",
  "currency": "USD",
  "underlying_symbol": "R_100",
  "duration": 5,
  "duration_unit": "m"
}));
```

Note: the symbol field is `underlying_symbol`.

### Step 3. Buy from the proposal id

```javascript
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.msg_type === 'proposal' && msg.proposal?.id) {
    ws.send(JSON.stringify({ "buy": msg.proposal.id, "price": msg.proposal.ask_price }));
  }
};
```

## Bulk purchase (REST, PAT auth — no Bearer)

```bash
curl -X POST https://api.derivws.com/trading/v1/options/contracts/bulk-purchase/real \
  -H "Deriv-App-ID: <app_id>" \
  -H "Content-Type: application/json" \
  -d '{"contract_parameters":{"amount":10,"contract_type":"CALL","currency":"USD","underlying_symbol":"R_100","duration":5,"duration_unit":"m"},
       "accounts":[{"account_id":"<acct>","token":"<PAT>"}]}'
```

_Source: [examples](https://developers.deriv.com/llms/examples.md)._
