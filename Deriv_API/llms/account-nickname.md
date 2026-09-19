# Account Nickname

**Auth:** required (scopes: account_manage)

Request for the GET /account/v1/nickname endpoint. Requires the Authorization header, plus Deriv-App-ID when authenticating with a Personal Access Token (PAT); takes no query parameters or body. The caller's brand and identity are resolved by the gateway from the X-Brand and X-Client-ID request headers and cannot be spoofed by the client.

**Endpoint:** `GET /account/v1/nickname`

**Status codes:** 200, 400, 401, 403, 404, 504


| Surface | Gateway | Auth |
|---------|---------|------|
| Public market data | `wss://api.derivws.com/trading/v1/options/ws/public` | None — connect directly |
| Authenticated trading | OTP-issued `wss://api.derivws.com/trading/v1/options/ws/real` or `/ws/demo` | OTP URL from `POST /trading/v1/options/accounts/{accountId}/otp` |

Public market data needs no auth. Authenticated trading uses an OTP URL (issued from a REST call with your Bearer token — OAuth 2.0 or PAT; PAT auth also sends `Deriv-App-ID`), then connect to that URL and send messages directly. The symbol field is `underlying_symbol`. See [authentication](https://developers.deriv.com/llms/authentication.md).

- Request schema: [`account_nickname_request.schema.json`](https://developers.deriv.com/schemas/account_nickname_request.schema.json)
- Response schema: [`account_nickname_response.schema.json`](https://developers.deriv.com/schemas/account_nickname_response.schema.json)

## Example

```bash
curl -X GET "https://api.derivws.com/account/v1/nickname" \
  -H "Authorization: Bearer <oauth_token>"
# Add -H "Deriv-App-ID: <app_id>" when authenticating with a Personal Access Token (PAT).
```

## Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `headers` | object | Yes |  |

### `headers`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Deriv-App-ID` | string | Yes | Application identifier. Required for Personal Access Token (PAT) authentication; not required for OAuth Bearer tokens. |
| `Authorization` | string | Yes | Bearer token for authentication |

## Response

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data` | object | Yes | Nickname data for the authenticated user's identity. |
| `errors` | array | Yes | Empty on success. |
| `metadata` | object | Yes | Request metadata included in every response. |

### `data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `external_reference_id` | string, (uuid) | Yes | The external reference ID for this identity. |
| `nickname` | string | Yes | The nickname associated with this identity. |

### `errors`

Array of `items`.

### `metadata`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | The request URI. |
| `method` | string: ["GET","POST","PUT","DELETE","PATCH"] | Yes | The HTTP method used for the request. |
| `timing` | number | Yes | Time in seconds for the service to process the request. |

_Source: [account-nickname](https://developers.deriv.com/llms/account-nickname.md)._
