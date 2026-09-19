# API Overview

**This documents the Deriv API.** If a field or endpoint is not documented here, it does not exist in the API.

## Base URLs

- REST base: `https://api.derivws.com`
- OAuth authorization: `https://auth.deriv.com/oauth2/auth`
- OAuth token: `https://auth.deriv.com/oauth2/token`

## Gateways

- **WebSocket (public market data):** `wss://api.derivws.com/trading/v1/options/ws/public` — no authentication, no request body. Use for `ticks`, `active_symbols`, `proposal`, `time`, `trading_times`.
- **WebSocket (authenticated trading):** obtained from `POST /trading/v1/options/accounts/{accountId}/otp`, which returns a one-time-password WebSocket URL (`wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo`). Connect to that URL and send messages directly.
- **REST:** `https://api.derivws.com` — authenticated calls require `Authorization: Bearer <token>` (plus `Deriv-App-ID` when using PAT authentication). Base paths: `/trading/v1/options/` (accounts, OTP, contracts), `/wallet/v1/` (Wallet balances, transactions, transfers), `/payment-agents/v1/`, `/partners/` (partner analytics, client tags), `/account/v1/`, `/applications/v1/`.

## Auth model summary

- OAuth2 Authorization Code + PKCE → Bearer access token.
- REST trading calls: `Authorization: Bearer` (plus `Deriv-App-ID` for PAT auth).
- WebSocket trading: exchange the Bearer token for an OTP URL via `POST .../otp`, then connect.
- Bulk-purchase: `Deriv-App-ID` + per-account PATs (no Bearer).
- Wallet and payment-agent calls: `Authorization: Bearer` carrying the `payment` scope (plus `Deriv-App-ID` for PAT auth). A token without `payment` scope is rejected with `403`.
- Partners calls: `Authorization: Bearer` carrying the `application_read` scope (plus `Deriv-App-ID` for PAT auth). A token without `application_read` scope is rejected with `403`.

See [authentication](https://developers.deriv.com/llms/authentication.md) for the full flow.

## Rate limits

- **WebSocket:** 100 requests per second per connection
- **REST API:** 60 requests per minute per token
- **Subscription limit:** 100 active subscriptions per connection
- **Connection limit:** 5 concurrent WebSocket connections per user

## Resources

- **Documentation:** https://developers.deriv.com/docs/
- **Interactive Playground:** https://developers.deriv.com/playground
- **Support:** api-support@deriv.com

_Source: [api-overview](https://developers.deriv.com/llms/api-overview.md)._
