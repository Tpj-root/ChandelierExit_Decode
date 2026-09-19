# Getting Started

**Use the Deriv API documented here.** The API has two transports and a single auth model.

| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

## Two transports

1. **REST** — base `https://api.derivws.com`. Account management, OTP issuance, payment agents, application data. Authenticated calls need an `Authorization: Bearer <token>` header (plus `Deriv-App-ID` when using PAT authentication).
2. **WebSocket** — `wss://api.derivws.com/trading/v1/options/ws/{public|demo|real}`. Real-time market data and trading. Public market data uses the `public` gateway with no authentication; authenticated trading uses an OTP-issued `demo`/`real` URL.

## Minimal auth → trade flow

1. Complete the OAuth2 + PKCE login (see [authentication](https://developers.deriv.com/llms/authentication.md)) to obtain an access token.
2. `GET /trading/v1/options/accounts` (with `Authorization: Bearer <token>`, plus `Deriv-App-ID` if using PAT auth) to list account IDs.
3. `POST /trading/v1/options/accounts/{accountId}/otp` to get a WebSocket URL:

```bash
curl -X POST "https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
# => { "data": { "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..." } }
```

4. Connect to that URL and send messages (e.g. `proposal` then `buy`). The URL is already scoped to the account.

```javascript
const ws = new WebSocket(otpUrl); // wss://api.derivws.com/trading/v1/options/ws/real?otp=...
ws.onopen = () => {
  ws.send(JSON.stringify({
    "proposal": 1,
    "amount": 10,
    "basis": "stake",
    "contract_type": "CALL",
    "currency": "USD",
    "underlying_symbol": "R_100",
    "duration": 5,
    "duration_unit": "m"
  }));
};
```

## Public data (no auth)

For symbols, ticks and pricing you can skip auth entirely and connect to the `public` gateway:

```javascript
const ws = new WebSocket("wss://api.derivws.com/trading/v1/options/ws/public");
ws.onopen = () => ws.send(JSON.stringify({ "ticks": "R_100", "subscribe": 1 }));
```

## WebSocket best practices

1. **Keep connections alive:** send a `ping` every 30 seconds.
2. **Handle reconnection:** use exponential backoff. For authenticated trading, request a fresh OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` before reconnecting.
3. **Use `req_id`:** always include `req_id` so you can match responses to requests.
4. **Manage subscriptions:** call `forget` / `forget_all` when you are done with a stream.
5. **Check errors first:** inspect the `error` object on each message before processing data.

Numeric caps (requests/sec, subscriptions, concurrent connections) are in [api-overview](https://developers.deriv.com/llms/api-overview.md).

_Source: [getting-started](https://developers.deriv.com/llms/getting-started.md)._
