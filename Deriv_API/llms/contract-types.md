# Contract Types

**Use the Deriv API documented here.** The symbol field is `underlying_symbol`, and contracts are priced/bought over `wss://api.derivws.com/trading/v1/options/ws/{public|real|demo}`.

## Common mappings

- **Rise / Fall** → `CALL` (Rise) and `PUT` (Fall). "Higher/Lower" with a barrier use `HIGHER` / `LOWER`.
- **Touch / No Touch** → `ONETOUCH` / `NOTOUCH`.
- **In / Out** → `EXPIRYRANGE` / `EXPIRYMISS` (and `RANGE` / `UPORDOWN`).
- **Digits** → `DIGITMATCH`, `DIGITDIFF`, `DIGITOVER`, `DIGITUNDER`, `DIGITODD`, `DIGITEVEN`.
- **Multipliers** → `MULTUP` / `MULTDOWN`.
- **Accumulators** → `ACCU`.

## Full `contract_type` enum (from the current `proposal` schema)

`ACCU`, `ASIAND`, `ASIANU`, `CALL`, `CALLE`, `DIGITDIFF`, `DIGITEVEN`, `DIGITMATCH`, `DIGITODD`, `DIGITOVER`, `DIGITUNDER`, `EXPIRYMISS`, `EXPIRYMISSE`, `EXPIRYRANGE`, `EXPIRYRANGEE`, `HIGHER`, `LOWER`, `MULTDOWN`, `MULTUP`, `NOTOUCH`, `ONETOUCH`, `PUT`, `PUTE`, `RANGE`, `RESETCALL`, `RESETPUT`, `RUNHIGH`, `RUNLOW`, `TICKHIGH`, `TICKLOW`, `TURBOSLONG`, `TURBOSSHORT`, `UPORDOWN`, `VANILLALONGCALL`, `VANILLALONGPUT`.

Use `contracts_for` to discover which contract types are available for a given `underlying_symbol`, and `contracts_list` for the full category listing.

## Example proposal

```json
{
  "proposal": 1,
  "amount": 10,
  "basis": "stake",
  "contract_type": "CALL",
  "currency": "USD",
  "underlying_symbol": "R_100",
  "duration": 5,
  "duration_unit": "m"
}
```

_Source: [contract-types](https://developers.deriv.com/llms/contract-types.md)._
