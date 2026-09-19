# Error Handling

**Use the Deriv API documented here.** The API is OTP-authenticated for WebSocket trading.

## REST errors

REST endpoints return a structured envelope with an `errors` array and a `meta` block. The HTTP status mirrors the error `status`:

```json
{
  "errors": [
    {
      "status": 400,
      "code": "ValidationError",
      "message": "date_from is required"
    }
  ],
  "meta": {
    "endpoint": "/applications/v1/markup-statistics",
    "method": "GET",
    "timing": 12
  }
}
```

Common statuses: `400` bad request/validation, `401` unauthorized (missing/invalid token, or missing `Deriv-App-ID` when authenticating with a PAT), `403` forbidden (valid token, insufficient scope), `404` not found, `409` conflict, `422` unprocessable entity, `429` rate limited (see [api-overview](https://developers.deriv.com/llms/api-overview.md) for concrete limits), `500` internal error, `502`/`503`/`504` upstream issues. Show generic messages to end users; log details server-side only.

## WebSocket errors

WebSocket responses carry an `error` object with a `code` and `message` alongside the `msg_type` of the originating call:

```json
{
  "error": { "code": "InputValidationFailed", "message": "Missing required parameter underlying_symbol" },
  "msg_type": "proposal"
}
```

If a connection is rejected or the OTP has expired, request a fresh OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` and reconnect.

## Common error codes

- `InvalidToken` — token is invalid or expired
- `RateLimit` — too many requests (see [api-overview](https://developers.deriv.com/llms/api-overview.md) for limits)
- `InputValidationFailed` — invalid request parameters
- `ContractNotFound` — contract does not exist
- `InsufficientBalance` — not enough funds
- `ValidationError` — field validation failed
- `NotFound` — resource not found
- `Unauthorized` — authentication failed
- `InternalError` — server error

## Retries

- Retry idempotent reads (`active_symbols`, `ticks_history`, `GET` calls) with exponential backoff.
- Do **not** blindly retry trades (`buy`, `sell`, bulk-purchase). Use the returned `transaction_id` / `contract_id` to confirm state before retrying.

_Source: [errors](https://developers.deriv.com/llms/errors.md)._
