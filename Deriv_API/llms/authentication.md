# Authentication

**Use the Deriv API documented here.** The auth model is OAuth2 for REST, plus an OTP-URL flow for WebSocket trading. There is no auth handshake on the WebSocket itself.

| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

## OAuth 2.0 (Authorization Code + PKCE)

Obtain an OAuth2 access token via the Authorization Code flow with PKCE.

- Authorization endpoint: `https://auth.deriv.com/oauth2/auth`
- Token endpoint: `https://auth.deriv.com/oauth2/token`

The access token is sent as `Authorization: Bearer <token>` on REST calls.

Login, signup, and troubleshooting: [oauth](https://developers.deriv.com/llms/oauth.md).

## REST request headers

Authenticated REST requests require an `Authorization: Bearer <token>` header (OAuth 2.0 access token or Personal Access Token).

- **PAT authentication:** requires the `Deriv-App-ID` header; omitting it returns `401 "Deriv-App-ID header is required for PAT tokens"`.
- **OAuth 2.0:** `Deriv-App-ID` is not required because the OAuth access token already identifies the client application.

```
Authorization: Bearer <token>
Deriv-App-ID: <your app id>    # Required for PAT authentication only
Content-Type: application/json # For POST/PUT/PATCH requests
```

## WebSocket authentication — the OTP-URL flow

Authentication happens before connect:

1. Call `POST /trading/v1/options/accounts/{accountId}/otp` with an `Authorization: Bearer <token>` header (plus `Deriv-App-ID` if using PAT auth).
2. The response returns a `data.url` — a WebSocket URL with an embedded one-time password.
3. Connect to that URL directly. Do not send any auth message after connect.

```
POST https://api.derivws.com/trading/v1/options/accounts/{accountId}/otp
Headers: Authorization: Bearer <token>   # plus Deriv-App-ID for PAT auth
Response: { "data": { "url": "wss://api.derivws.com/trading/v1/options/ws/real?otp=..." } }
```

Then: `new WebSocket(otpUrl)` — no further auth step.

## Public market data (no authentication)

Connect directly to `wss://api.derivws.com/trading/v1/options/ws/public` — no OTP, no token, no request body. Use this for `ticks`, `active_symbols`, `proposal` (pricing), `time`, `trading_times`.

## OAuth scopes

The Bearer token must carry the scope the endpoint declares, or the call is rejected with `403` even though the token is valid.

| Scope | Grants |
|-------|--------|
| `payment` | Wallet balances, transactions and transfers (`/wallet/v1/*`), and all payment-agent calls (`/payment-agents/v1/*`) |
| `trade` | Options trading, contract status, and the Options Trading (Legacy) endpoints |
| `account_manage` | Creating an Options Trading account, and reading the account nickname |
| `application_read` | Markup statistics for your registered applications |

Most WebSocket calls and the public REST endpoints declare no scope; the table covers the endpoints that do. Request every scope your integration needs at authorisation time — a token cannot gain one afterwards without sending the user through OAuth again.

## Wallet requests

`/wallet/v1/*` uses standard REST headers with a `payment`-scoped token (plus `Deriv-App-ID` if using PAT auth). Nothing wallet-specific is sent on the wire:

```
GET https://api.derivws.com/wallet/v1/wallets
Headers: Authorization: Bearer <payment-scoped token>   # plus Deriv-App-ID for PAT auth
```

The transfer endpoints add two request-body conventions rather than auth ones:

- `request_id` is an idempotency key — resubmitting one you have already used does not create a second transfer.
- A cross-currency transfer carries an `exchange_rate` and its `rate_token`, both taken from `GET /wallet/v1/exchange-rate`.

## Bulk-purchase authentication (different)

`POST /trading/v1/options/contracts/bulk-purchase/{real,demo}` uses the `Deriv-App-ID` header plus per-account Personal Access Tokens (PATs) in the request body. **Never** send an OAuth Bearer token to bulk-purchase.

_Source: [authentication](https://developers.deriv.com/llms/authentication.md)._
