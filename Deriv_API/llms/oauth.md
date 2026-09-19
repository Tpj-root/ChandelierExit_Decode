# OAuth 2.0 Reference

OAuth2 Authorization Code flow with PKCE is used to obtain the access token that authenticates Deriv REST and OTP calls.

## Endpoints

- Authorization: `https://auth.deriv.com/oauth2/auth`
- Token: `https://auth.deriv.com/oauth2/token`

## PKCE flow

1. Generate a `code_verifier` (random 43–128 character string) and `code_challenge` = SHA256(code_verifier), `code_challenge_method=S256`.
2. Redirect the user to the authorization endpoint with `client_id` (= your App ID), `response_type=code`, `redirect_uri`, `scope`, `state`, `code_challenge`, `code_challenge_method`.
3. After login, the callback receives `code`.
4. Exchange `code` at the token endpoint (from your **backend**, never the browser): POST `grant_type=authorization_code`, `code`, `redirect_uri`, `client_id`, `code_verifier`.
5. Receive `access_token` (and `refresh_token`). Use the access token as `Authorization: Bearer <token>`.

### PKCE generation (JavaScript)

```javascript
function base64UrlEncode(buffer) {
  return btoa(String.fromCharCode(...new Uint8Array(buffer)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

async function createPkce() {
  const verifierBytes = crypto.getRandomValues(new Uint8Array(32));
  const code_verifier = base64UrlEncode(verifierBytes);
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(code_verifier),
  );
  const code_challenge = base64UrlEncode(digest);
  return { code_verifier, code_challenge, code_challenge_method: "S256" };
}
```

### Token exchange

```http
POST https://auth.deriv.com/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id=YOUR_CLIENT_ID
&code=AUTHORIZATION_CODE
&redirect_uri=https://yourapp.com/callback
&code_verifier=YOUR_CODE_VERIFIER
```

## Login

Redirect users to the authorization endpoint with these parameters:

| Parameter | Required | Value / Description |
|-----------|----------|---------------------|
| `response_type` | Yes | `code` |
| `client_id` | Yes | Your registered OAuth2 application ID (same as `Deriv-App-ID`) |
| `redirect_uri` | Yes | Must exactly match the URI registered with Deriv |
| `scope` | Yes | Space-separated list of the scopes your integration needs: `trade`, `payment`, `account_manage`, `application_read`. See [authentication](https://developers.deriv.com/llms/authentication.md) for what each grants. |
| `state` | Yes | Random string for CSRF protection — generate fresh for each request |
| `code_challenge` | Yes | BASE64URL(SHA256(code_verifier)) |
| `code_challenge_method` | Yes | `S256` |

Example:

```
https://auth.deriv.com/oauth2/auth?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://yourapp.com/callback&scope=trade+account_manage&state=RANDOM_STATE&code_challenge=PKCE_CHALLENGE&code_challenge_method=S256
```

## Sign up

Same base URL and parameters as login, plus:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `prompt` | Yes | Set to `registration` to show the signup form instead of login |
| `sidc` | No | Session ID (GUID) from the Deriv partner dashboard, used for tracking |
| `utm_campaign` | No | Campaign name for analytics |
| `utm_medium` | No | Set to `affiliate` for partner integrations |
| `utm_source` | No | Your affiliate ID from the Deriv partner dashboard |

Partner attribution also accepts these equivalent parameter names: `t`, `affiliate_token`, `sidi`, and `ca`. Use the exact name from your referral link or Partners dashboard — do not include more than one.

Example:

```
https://auth.deriv.com/oauth2/auth?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://yourapp.com/callback&scope=trade+account_manage&state=RANDOM_STATE&code_challenge=PKCE_CHALLENGE&code_challenge_method=S256&prompt=registration&sidc=YOUR_SESSION_GUID&utm_campaign=YOUR_CAMPAIGN&utm_medium=affiliate&utm_source=YOUR_AFFILIATE_ID
```

## Callback

After authentication, Deriv redirects to your `redirect_uri`:

- **Success:** `https://yourapp.com/callback?code=AUTHORIZATION_CODE&state=RANDOM_STATE`
- **Error:** `https://yourapp.com/callback?error=access_denied&error_description=User+cancelled`

Your app must verify `state` matches the value stored before the redirect, then exchange `code` immediately (single-use, short-lived) via the token endpoint on your backend.

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| State mismatch error | `state` in callback doesn't match stored value | Store `state` in `sessionStorage` before redirecting |
| `invalid_grant` on token exchange | `code_verifier` doesn't match the challenge, or code expired | Send the original `code_verifier`, not a new one; exchange immediately |
| Redirect URI mismatch | URL doesn't exactly match registration | Check trailing slashes, http vs https, port numbers |
| `invalid_client` | Wrong `client_id` | Verify credentials from the Deriv dashboard |
| Login form shows instead of signup | Missing `prompt=registration` | Add `prompt=registration` to the authorization URL |
| Signup not tracked to partner | Missing or wrong UTM / `sidc` / alias | Verify `sidc` or `t` / `affiliate_token` / `sidi` / `ca`, plus `utm_*` |

## Headers on authenticated REST calls

```
Authorization: Bearer <access_token>
```

`Deriv-App-ID` is not required here — the OAuth access token already identifies the client application. Send it only when authenticating with a Personal Access Token (PAT); see [authentication](https://developers.deriv.com/llms/authentication.md).

The App ID (`Deriv-App-ID`) and the OAuth `client_id` are the same application identifier issued in the Deriv dashboard.

## Notes

- Access tokens are never sent to the bulk-purchase endpoints — those use per-account PATs.
- WebSocket trading does not take the token directly; use the token to obtain an OTP WebSocket URL via `POST /trading/v1/options/accounts/{accountId}/otp` (see [authentication](https://developers.deriv.com/llms/authentication.md)).

_Source: [oauth](https://developers.deriv.com/llms/oauth.md)._
