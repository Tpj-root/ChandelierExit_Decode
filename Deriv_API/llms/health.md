# Health Check

**Auth:** not required

GET /v1/health requires no request body or parameters.

**Endpoint:** `GET /v1/health`

**Status codes:** 200


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`health_request.schema.json`](https://developers.deriv.com/schemas/health_request.schema.json)
- Response schema: [`health_response.schema.json`](https://developers.deriv.com/schemas/health_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/v1/health"
```

## Request

_Source: [health](https://developers.deriv.com/llms/health.md)._
