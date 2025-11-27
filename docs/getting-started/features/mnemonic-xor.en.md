# What is Mnemonic XOR?

It is an implementation of the XOR ([exclusive OR](https://en.wikipedia.org/wiki/Exclusive_or)) operation across the entropy values of two or more mnemonics to produce a combined result, based on [Coinkite's SeedXOR](https://github.com/Coldcard/firmware/blob/master/docs/seed-xor.md).

## How It Works

Krux derives a new mnemonic (and therefore a new seed) by performing an XOR operation on the **entropy bytes** of the source mnemonics. The result of this XOR operation is a new set of **entropy bytes**, which is then converted into a new mnemonic - and subsequently, a new seed.

<img src="/krux/img/mnemonic_xor.png" align="center">

- Obtain two different mnemonics (A and B) and extract their **entropy bytes**.
- Validate the input entropies to prevent redundant or unsafe operations:

    - `A XOR B = A`: indicates that B consists entirely of zeros (useless - no change to the result).
    - `A XOR B = A'`, where `A'` is the bitwise complement of `A`: indicates that B consists entirely of ones (dangerous - produces a predictable inverse).

- Ensure that both mnemonics have the same length before proceeding.
- Perform the XOR operation between **entropy bytes** from `A` and `B`.
- Validate the resulting entropy `C` (same checks as above).
- Convert the valid **entropy bytes** `C` into a new mnemonic `C`.
- Optionally, the user may apply a password to derive a new master seed.

---

## Split and Recover Parts (or "shares")

A mnemonic can be split into two separate parts (or "shares") using the XOR operation. Each share by itself reveals nothing about the original secret. The original mnemonic can only be reconstructed when **both shares are combined**.

### Core Principle

This method relies on a fundamental property of XOR:

If `A XOR B = C`, then `B XOR C = A`.

- **A**: The original mnemonic (the secret to protect)
- **B**: A newly generated random mnemonic (Share 1)
- **C**: The mnemonic produced by the XOR operation (Share 2)

### Step-by-Step Guide to Splitting Your Mnemonic

#### Phase 1: Splitting Process

##### Generate a Random Share (Mnemonic B)

1. Generate a new random mnemonic using dice rolls or an image.
2. **Important:** This mnemonic must have the same number of words (12 or 24) as your original mnemonic `A`.

##### Back Up Mnemonic B
- Use a reliable and secure method to back up mnemonic `B`.

##### Perform the XOR Operation

1. Load mnemonic `A`.
2. Navigate to **Wallet -> Mnemonic XOR**.
3. Load mnemonic `B` to be XORed with `A`.
4. The resulting entropy from `A XOR B` will be used to generate the second share - mnemonic `C`.

##### Back Up Mnemonic C
- Go to **Backup** and securely store mnemonic `C` using your preferred backup method.

#### Phase 2: Verification & Finalization
Don't trust, verify!

1. Retrieve your backups of mnemonics `B` and `C`.
2. Load one of them and XOR it with the other.
3. Confirm that the resulting mnemonic matches the original mnemonic `A`.

⚠️ **Only after successful verification** should you securely destroy the original mnemonic `A`.

#### Important Notes

- **Keep shares separate:** Store mnemonics `B` and `C` in different secure locations.
- **Both shares required:** Neither share alone reveals any information about the original mnemonic.
- **Always verify!:** Test the recovery process before destroying the original.
- **Matching word count:** All three mnemonics (`A`, `B`, and `C`) must have the same number of words.
