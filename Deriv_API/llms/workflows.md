# Workflows

Current API only. WebSocket trading uses the OTP-URL flow.

## Propose → Buy → Monitor → Sell

1. **Authenticate:** OAuth2 → Bearer token → `POST /trading/v1/options/accounts/{accountId}/otp` → connect to the returned WebSocket URL.
2. **Propose:** send `{ proposal: 1, amount, basis, contract_type, currency, underlying_symbol, duration, duration_unit }`. (The symbol field is `underlying_symbol`.)
3. **Buy:** on the `proposal` response, send `{ buy: <proposal.id>, price: <ask_price> }`. Receive `contract_id`.
4. **Monitor:** subscribe with `{ proposal_open_contract: 1, contract_id, subscribe: 1 }` for live status.
5. **Sell:** before expiry, send `{ sell: <contract_id>, price: <min_price_or_0> }`.

## Real-time balance and portfolio

Both require authentication, so first exchange your OAuth token for an OTP WebSocket URL:

```bash
curl -X POST "https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
# => { "data": { "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..." } }
```

Then connect to the returned URL and subscribe:

```javascript
const ws = new WebSocket(otpUrl); // wss://api.derivws.com/trading/v1/options/ws/real?otp=...
ws.onopen = () => {
  ws.send(JSON.stringify({ "balance": 1, "subscribe": 1 }));
  ws.send(JSON.stringify({ "portfolio": 1 }));
};
```

## Public data stream (no auth)

```javascript
const ws = new WebSocket('wss://api.derivws.com/trading/v1/options/ws/public');
ws.onopen = () => {
  ws.send(JSON.stringify({ "active_symbols": "brief" }));
  ws.send(JSON.stringify({ "ticks": "R_100", "subscribe": 1 }));
};
// active_symbols returns underlying_symbol / underlying_symbol_name / underlying_symbol_type
```

## Unsubscribe

```javascript
ws.send(JSON.stringify({ "forget": "<subscription id>" }));
ws.send(JSON.stringify({ "forget_all": "ticks" }));
```

_Source: [workflows](https://developers.deriv.com/llms/workflows.md)._
