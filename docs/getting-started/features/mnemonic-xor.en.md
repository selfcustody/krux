# What's the Mnemonic XOR?

It's a implementation of [XOR logical gate](https://www.geeksforgeeks.org/digital-logic/xor-gate/) to operate, indefinitely, an [exclusive OR](https://en.wikipedia.org/wiki/Exclusive_or) upon a loaded mnemonic, based on [Coinkite's SeedXOR](https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md).

# How it works

To derive a new mnemonic (and thus, a new seed) from other mnemonics, an operation occurs with the **mnemonic's entropy bytes**.
Operate a XOR between them will derive a new **entropy bytes** that will be converted to a new mnemonic and then, to a new seed:

<img src="../../../img/mnemonic_xor.png" align="center">

- We get two different mnemonics (A and B), extract their *entropy bytes*;
- validate the input entropies to avoid useless or dangerous operations:
  - `A XOR B = A`: it will not change the XORed mnemonic;
  - `A XOR B = A'` where `A'` is a "inverse" version of `A`;
- once the inputs are checked, krux will apply a XOR between the *entropy bytes*;
- validate the output entropy (same as above);
- "convert" the valid *entropy bytes* output to a new mnemonic (C);
- the user then can apply a password (optional) and get a new **master seed**.

# Split and recover shares

You can split a mnemonic into two separate mnemonics (or "shares") using the XOR operation. Neither share reveals any information about the original secret on its own. The original mnemonic can only be recovered when **both shares are combined**.

### Core Principle

Now we show a basic step
If `A XOR B = C`, then `B XOR C = A`.

- **A**: Your original mnemonic (the secret to protect);
- **B**: A newly generated, random mnemonic (Share 1);
- **C**: The resulting mnemonic from the XOR operation (Share 2).

---

## Step-by-Step Guide to Splitting Your Mnemonic

### Phase 1: The Splitting Process

#### Step 1: Generate a Random Share (Mnemonic B)

1. Generate a new, random mnemonic from dice rolls or an image;
2. **CRITICAL**: This mnemonic must have the same number of words (12 or 24) as your original mnemonic (A).

#### Step 2: Backup Mnemonic B

- Use a safe method to backup mnemonic B.

#### Step 3: Perform the XOR Operation

1. Load mnemonic A, go to **Wallet -> Mnemonic XOR** and load mnemonic B to be XORed with A;
2. The resulting entropy of `A XOR B` will be used to create the second share, mnemonic C.

#### Step 4: Back Up Mnemonic C

1. Go to **Backup** and choose your favorite secure method to backup mnemonic C
---

### Phase 2: Verification & Finalization

> ⚠️ **DO NOT SKIP THIS PHASE**

#### Step 5: Verify the Recovery Process

**This is non-negotiable.** Before relying on the system or destroying the original mnemonic, perform a test:

1. Retrieve mnemonic B and C backups;
2. Load one of them and XOR it with the other;
3. Verify that the resulting mnemonic matches the original mnemonic A.

#### Step 6: Destroy the Original

⚠️ **Only after you have successfully verified in Step 5** that the recovery works perfectly should you securely destroy the original mnemonic (A).

---

## Important Notes

- **Keep shares separate**: Store mnemonic B and mnemonic C in different secure locations;
- **Both shares required**: Neither share alone provides any information about the original mnemonic;
- **Always verify**: Test the recovery process before destroying the original;
- **Same word count**: All three mnemonics (A, B, and C) must have the same number of words.
