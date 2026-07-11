# CoinJoin Signing

CoinJoin is a privacy tool where several people build one Bitcoin transaction together. The result makes it harder to link which input paid which output.

Krux can help with this flow by proving that your wallet controls an input and by signing a CoinJoin transaction only when the transaction fits a safety policy.

## What Krux Checks

CoinJoin signing is separate from normal PSBT signing. Krux does not treat the full transaction as your spend. Instead, it checks:

- how much value comes from your own inputs;
- how much value returns to your own wallet;
- how much value can be lost to fees or coordinator costs;
- whether the transaction uses supported script types;
- whether the request matches the approved wallet and account.

If the returned amount is below the configured safety limit, Krux rejects the signing request.

## Supported Wallet Types

The first version supports:

- Native Segwit single-sig wallets;
- Taproot single-sig wallets.

Multisig and Miniscript CoinJoin signing are not part of this feature.

## Policy-Based Approval

CoinJoin signing is disabled by default. A user must enable it and approve a policy before unattended signing can happen.

The policy can limit:

- the wallet fingerprint;
- the account path;
- the allowed script types;
- the minimum self-transfer percentage;
- the maximum effective fee rate for your own registered inputs.

The `Min self-transfer %` setting defaults to 95. That means Krux expects at least 95% of your own input value to return to your own wallet unless you configure a stricter or looser policy.

## CoinJoin Process

A CoinJoin flow usually has these steps:

1. Your wallet asks Krux to prove that it controls the coins being registered.
2. The coordinator builds a round with inputs and outputs from several people.
3. Your wallet sends the CoinJoin PSBT to Krux.
4. Krux checks the transaction against your CoinJoin policy.
5. Krux signs only if the transaction stays inside your limits.

You can personalize the policy with:

- `Max fee rate sat/vB`: the highest effective fee rate Krux allows for your own registered inputs. The default is 5 sat/vB.
- `Max rounds`: the maximum number of CoinJoin rounds your setup may run before asking you to approve again. The default is 210.
- `Min self-transfer %`: the minimum share of your own input value that must return to your own wallet. Higher values are stricter. The default is 95%.

If any step goes outside these limits, Krux refuses to sign.

## Ownership Proofs

Some CoinJoin coordinators ask the wallet to prove that it controls an input before joining a round. Krux can create this proof without spending coins.

This proof is not a normal message signature and it is not a transaction signature. It is only used by the CoinJoin flow to register an input.

## Companion Software

Krux provides the firmware-side support and a request format that companion software can use. A wallet or bridge still needs to send the proof request and the CoinJoin PSBT to Krux.

Normal PSBT signing remains unchanged. If you are not using compatible companion software, this feature does not change your regular signing workflow.
