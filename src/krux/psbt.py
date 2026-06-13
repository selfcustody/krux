# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import gc
from embit.psbt import CompressMode
from embit.silent_payments import SilentPaymentsPSBT as PSBT
from uUR import UR, Types
from .baseconv import base_decode
from .krux_settings import t
from .settings import THIN_SPACE, ELLIPSIS
from .qr import FORMAT_PMOFN, FORMAT_BBQR
from .key import Key, P2SH, P2SH_P2WPKH, P2SH_P2WSH, P2WPKH, P2WSH, P2TR
from .sats_vb import SatsVB

# PSBT Output Types:
CHANGE = 0
SELF_TRANSFER = 1
SPEND = 2

# We always uses thin spaces after the ₿ in this file
BTC_SYMBOL = "₿"

MAX_POLICY_COSIGNERS_DISPLAYED = 5


class Counter(dict):
    """Helper class for dict"""

    def __getitem__(self, key):
        """Avoids error when key is missing"""
        return self.get(key, 0)


class PSBTSigner:
    """Responsible for validating and signing PSBTs"""

    def __init__(self, wallet, psbt_data, qr_format, psbt_filename=None):
        self.wallet = wallet
        self.base_encoding = None
        self.ur_type = None
        self.qr_format = qr_format
        self.policy = None
        self.is_b64_file = False
        self._has_sp = False

        # Parse the PSBT
        if psbt_filename:
            gc.collect()
            from .settings import SD_PATH

            file_path = "/%s/%s" % (SD_PATH, psbt_filename)
            try:
                with open(file_path, "rb") as file:
                    self.psbt = PSBT.read_from(file)
                self.validate()
            except:
                try:
                    self.policy = None  # Reset policy
                    self.is_b64_file = self.file_is_base64_encoded(file_path)
                    if self.is_b64_file:
                        # BlueWallet exports PSBTs as base64 encoded files
                        # So it will be decoded and loaded uncompressed
                        with open(file_path, "r") as file:
                            psbt_data = file.read()
                        self.psbt = PSBT.parse(base_decode(psbt_data, 64))
                    else:
                        # Try to load the PSBT in compressed mode
                        with open(file_path, "rb") as file:
                            file.seek(0)  # Reset the file pointer to the beginning
                            self.psbt = PSBT.read_from(
                                file, compress=CompressMode.CLEAR_ALL
                            )
                except Exception as e:
                    raise ValueError("Error loading PSBT file: %s" % e)
            self.base_encoding = 64  # In case it is exported as QR code
        elif isinstance(psbt_data, UR):
            try:
                raw = Types.psbt_from_cbor(psbt_data.cbor)
                self.ur_type = Types.CRYPTO_PSBT_TYPE
                self.psbt = PSBT.parse(raw)
                del raw
                gc.collect()
                # self.base_encoding = 64
            except:
                raise ValueError("invalid PSBT")
        else:
            try:
                self.psbt = PSBT.parse(psbt_data)
                if self.qr_format == FORMAT_PMOFN:
                    # We can't return the PSBT as a multi-part sequence of bytes, so convert to
                    # base64 first
                    self.base_encoding = 64
            except:
                try:
                    self.psbt = PSBT.parse(base_decode(psbt_data, 64))
                    self.base_encoding = 64
                except:
                    try:
                        self.psbt = PSBT.parse(base_decode(psbt_data, 58))
                        self.base_encoding = 58
                    except:
                        try:
                            import base43

                            self.psbt = PSBT.parse(base43.decode(psbt_data))
                            self.base_encoding = 43
                        except:
                            raise ValueError("invalid PSBT")
        if self.policy is None:
            # If not yet validated (e.g. from file and compressed), validate now
            try:
                self.validate()
            except Exception as e:
                raise ValueError("Invalid PSBT: %s" % e)

    def file_is_base64_encoded(self, file_path, chunk_size=64):
        """Checks if a file is base64 encoded"""
        with open(file_path, "rb") as file:
            chunk = file.read(chunk_size)
            if not chunk:
                raise ValueError("Empty file")
            # Check if chunk length is divisible by 4
            if len(chunk) % 4 != 0:
                return False
            try:
                # Try to decode the chunk as base64
                base_decode(chunk.decode(), 64)
                return True
            except Exception:
                return False

    def validate(self):
        """Validates the PSBT"""
        # From: https://github.com/diybitcoinhardware/embit/blob/master/examples/change.py#L110
        xpubs = []
        origin_less_xpub = None
        try:
            xpubs, origin_less_xpub = self.xpubs()
        except:
            # Expected to fail to get xpubs from Miniscript PSBT
            pass
        for inp in self.psbt.inputs:
            # get policy of the input
            try:
                inp_policy = self.get_policy_from_psbt_input(
                    inp, xpubs, origin_less_xpub
                )
            except:
                raise ValueError("Unable to get policy")
            # if policy is None - assign current
            if self.policy is None:
                self.policy = inp_policy
            # otherwise check that everything in the policy is the same
            else:
                # check policy is the same
                if self.policy != inp_policy:
                    raise ValueError("mixed inputs in the tx")

        if self.wallet.is_miniscript():
            if not is_miniscript(self.policy):
                raise ValueError("Not a miniscript PSBT")
        elif self.wallet.is_multisig():
            if not is_multisig(self.policy):
                raise ValueError("Not a multisig PSBT")
        elif is_multisig(self.policy) or is_miniscript(self.policy):
            raise ValueError("Not a single-sig PSBT")

        # If a wallet descriptor has been loaded, verify that the wallet
        # policy matches the PSBT policy
        if self.wallet.is_loaded():
            if self.wallet.policy != self.policy:
                raise ValueError("policy mismatch")

        # BIP-375 Silent Payment validation lives in src/krux/silent_payments.py;
        # only fires when the PSBT actually carries SP outputs, so SP-naive
        # flows pay zero cost.
        self._has_sp = self.has_sp_outputs()
        if self._has_sp:
            # Only check policy eligibility at load time. Full BIP-375
            # structural validation (including ECDH-coverage) runs after
            # _populate_silent_payment_outputs() in sign(), because PSBTv2
            # outputs require placeholder scripts that trigger a false-positive
            # failure before ECDH shares are present.
            self._validate_silent_payment_eligibility()

    def has_sp_outputs(self):
        """Returns True if any output carries BIP-375 Silent Payment data"""
        from .silent_payments import has_sp_outputs

        return has_sp_outputs(self.psbt)

    def _silent_payment_address_from_output(self, out):
        """Delegates to silent_payments.address_from_output."""
        from .silent_payments import address_from_output

        return address_from_output(out, self.wallet.key.network)

    def _output_address(self, index, out):
        """Delegates to silent_payments.output_address."""
        from .silent_payments import output_address

        return output_address(self.psbt, index, out, self.wallet.key.network)

    def _validate_silent_payment(self, skip_output_scripts=True):
        """Delegates to silent_payments.validate."""
        from .silent_payments import validate as sp_validate

        sp_validate(self.psbt, skip_output_scripts=skip_output_scripts)

    def _validate_silent_payment_eligibility(self):
        """Delegates to silent_payments.validate_eligibility."""
        from .silent_payments import validate_eligibility

        validate_eligibility(self.policy)

    def get_policy_from_psbt_input(self, tx_input, xpubs, origin_less_xpub=None):
        """Extracts the scriptPubKey from an input's UTXO and determines the policy."""
        if tx_input.witness_utxo:
            scriptpubkey = tx_input.witness_utxo.script_pubkey
        elif tx_input.non_witness_utxo:
            # Retrieve the scriptPubKey from the specified output in the non_witness_utxo
            scriptpubkey = tx_input.non_witness_utxo.vout[tx_input.vout].script_pubkey
        else:
            raise ValueError("No UTXO information available in the input.")

        return get_policy(tx_input, scriptpubkey, xpubs, origin_less_xpub)

    def path_mismatch(self):
        """Verifies if the PSBT key path matches loaded keys's derivation path"""
        mismatched_paths = []
        der_path_nodes = len(self.wallet.key.derivation.split("/")) - 1
        for _input in self.psbt.inputs:
            if self.policy["type"] == P2TR:
                derivations = _input.taproot_bip32_derivations
            else:
                derivations = _input.bip32_derivations
            for pubkey in derivations:
                # Checks if fingerprint belongs to loaded key
                if self.policy["type"] == P2TR:
                    fingerprint = derivations[pubkey][1].fingerprint
                else:
                    fingerprint = derivations[pubkey].fingerprint
                if fingerprint != self.wallet.key.fingerprint:
                    # Not our key, won't check derivation path mismatch
                    continue
                if self.policy["type"] == P2TR:
                    derivation_path = derivations[pubkey][1].derivation
                else:
                    derivation_path = derivations[pubkey].derivation
                textual_path = "m"
                for index in derivation_path[:der_path_nodes]:
                    if index >= 2**31:
                        textual_path += "/{}h".format(index - 2**31)
                    else:
                        textual_path += "/{}".format(index)
                if textual_path != self.wallet.key.derivation:
                    if textual_path not in mismatched_paths:
                        mismatched_paths.append(textual_path)
        if mismatched_paths:
            return Key.format_derivation(", ".join(mismatched_paths))
        return ""

    def address_belongs_to_descriptor(self, psbt_output):
        """Check if the output is from our wallet descriptor"""

        if self.wallet.descriptor:
            return self.wallet.descriptor.owns(psbt_output)
        return False

    def _classify_output(self, out_policy, out):
        """Classify the output based on its properties and policy"""

        # Silent Payment outputs: detect outputs paying the wallet's own
        # BIP-352 address (scan AND label-tweaked spend key must both match,
        # so a foreign spend key paired with our scan key still shows as
        # SPEND). Everything else goes to an external recipient. This also
        # avoids deriving change/self-transfer state from an empty
        # script_pubkey.
        if getattr(out, "sp_data", None) is not None:
            from .silent_payments import own_sp_output_type

            own = own_sp_output_type(out, getattr(self.wallet.key, "sp_keys", None))
            if own == "change":
                return CHANGE
            if own == "self":
                return SELF_TRANSFER
            return SPEND

        address_from_my_wallet = False
        address_is_change = False
        # if policy is the same - probably change
        if out_policy == self.policy:
            # double-check that it's change
            # we already checked in get_cosigners and parse_multisig
            # that pubkeys are generated from cosigners,
            # and witness script is corresponding multisig
            # so we only need to check that scriptpubkey is generated from
            # witness script

            address_from_my_wallet = self.address_belongs_to_descriptor(out)

            if self.policy["type"] == P2TR:
                if address_from_my_wallet:
                    # _ = leafs
                    _, der = list(out.taproot_bip32_derivations.values())[0]
                    address_is_change = der.derivation[-2] == 1
            else:
                if address_from_my_wallet:
                    address_is_change = (
                        len(list(out.bip32_derivations.values())) > 0
                        and list(out.bip32_derivations.values())[0].derivation[-2] == 1
                    )
        if address_is_change:
            return CHANGE
        if address_from_my_wallet:
            return SELF_TRANSFER
        return SPEND

    def _btc_render(self, amount, prefix=" "):
        from .format import format_btc

        return prefix + BTC_SYMBOL + THIN_SPACE + "%s" % format_btc(amount)

    def _get_resume_fee(self, inp_amount, out_amount, output_policy_count):
        from .format import replace_decimal_separator

        fee = inp_amount - out_amount

        # fee percent with 1 decimal precision using math.ceil (minimum of 0.1)
        if out_amount > 0:
            fee_percent = max(
                0.1,
                (((fee * 10000 // out_amount) + 9) // 10) / 10,
            )
        else:
            fee_percent = 100.0

        resume_fee_str = (
            t("Fee:")
            + self._btc_render(fee)
            + " ("
            + replace_decimal_separator("%.1f" % fee_percent)
            + "%)"
        )
        if not self.wallet.is_miniscript():
            satvb = fee / SatsVB.get_vbytes(
                self.policy,
                output_policy_count,
                len(self.psbt.inputs),
                len(self.psbt.outputs),
            )
            resume_fee_str += (" ~%.1f" % satvb) + " sat/vB"

        return resume_fee_str, fee_percent

    def _sequence_render(self, title, elements):
        from .format import format_address

        message_seq = []
        for i, out in enumerate(elements):
            message_seq.append(
                (("%d. " + title + " \n\n%s\n\n") % (i + 1, format_address(out[0])))
                + self._btc_render(out[1], prefix="")
            )
        return message_seq

    def outputs(self):
        """Returns a list of messages describing where amounts are going"""

        inp_amount = 0
        for inp in self.psbt.inputs:
            if inp.witness_utxo:
                inp_amount += inp.witness_utxo.value
            elif inp.non_witness_utxo:  # Legacy
                # Retrieve the value from the specified output in the non_witness_utxo
                inp_amount += inp.non_witness_utxo.vout[inp.vout].value
        resume_inputs_str = (
            (t("Inputs (%d):") % len(self.psbt.inputs))
            + self._btc_render(inp_amount)
            + "\n\n"
        )

        self_transfer_list = []
        change_list = []
        spend_list = []

        self_amount = 0
        change_amount = 0
        spend_amount = 0
        resume_spend_str = ""
        resume_self_or_change_str = ""

        output_policy_count = Counter()

        xpubs = []
        origin_less_xpub = None
        try:
            xpubs, origin_less_xpub = self.xpubs()
        except:
            # Expected to fail to get xpubs from Miniscript PSBT
            pass
        for i, out in enumerate(self.psbt.outputs):
            if getattr(out, "sp_data", None) is not None:
                # script_pubkey is empty until the sender derives it; skip the
                # policy lookup and rely on _classify_output's SP short-circuit.
                # SP outputs always land as P2TR, so count them for the fee/vB
                # estimate even though the script is not derived yet.
                output_policy_count[P2TR] += 1
                output_type = self._classify_output(None, out)
            else:
                out_policy = get_policy(
                    out, self.psbt.tx.vout[i].script_pubkey, xpubs, origin_less_xpub
                )
                output_policy_count[out_policy["type"]] += 1
                output_type = self._classify_output(out_policy, out)

            address = self._output_address(i, out)
            value = self.psbt.tx.vout[i].value

            if output_type == CHANGE:
                change_list.append((address, value))
                change_amount += value
            elif output_type == SELF_TRANSFER:
                self_transfer_list.append((address, value))
                self_amount += value
            else:  # Address is from other wallet
                spend_list.append((address, value))
                spend_amount += value

        if len(spend_list) > 0:
            resume_spend_str = (
                (t("Spend (%d):") % len(spend_list))
                + self._btc_render(spend_amount)
                + "\n\n"
            )

        if len(self_transfer_list) + len(change_list) > 0:
            resume_self_or_change_str = (
                (
                    t("Self-transfer or Change (%d):")
                    % (len(self_transfer_list) + len(change_list))
                )
                + self._btc_render(self_amount + change_amount)
                + "\n\n"
            )

        resume_fee_str, fee_percent = self._get_resume_fee(
            inp_amount, self_amount + change_amount + spend_amount, output_policy_count
        )

        messages = []
        # first screen - resume
        messages.append(
            resume_inputs_str
            + resume_spend_str
            + resume_self_or_change_str
            + resume_fee_str
        )

        # sequence of spend
        messages.extend(self._sequence_render(t("Spend:"), spend_list))

        # sequence of self_transfer
        messages.extend(self._sequence_render(t("Self-transfer:"), self_transfer_list))

        # sequence of change
        messages.extend(self._sequence_render(t("Change:"), change_list))

        return messages, fee_percent

    def check_sighash(self):
        """Check that all inputs use SIGHASH_ALL (or DEFAULT for taproot).

        Refuse to sign if any input requests a non-standard sighash type
        (SIGHASH_NONE, SIGHASH_SINGLE, ANYONECANPAY), as these can allow
        an attacker to redirect funds after signing.
        """
        from embit.transaction import SIGHASH

        safe_sighash = {None, SIGHASH.DEFAULT, SIGHASH.ALL}
        for i, inp in enumerate(self.psbt.inputs):
            if inp.sighash_type not in safe_sighash:
                sighash_val = inp.sighash_type
                raise ValueError(
                    "Input %d has non-standard sighash type: 0x%02x" % (i, sighash_val)
                )

    def _sp_aux_rand(self, wallet_nonce):
        """Generate 32-byte auxiliary randomness for DLEQ proof generation.

        Mixes time.ticks_us() with a pre-computed wallet_nonce so the output is
        unpredictable to any observer who does not know the wallet root private
        key — even if the timer source is weak or predictable.
        """
        import hashlib
        import time

        try:
            tick_val = time.ticks_us()
        except AttributeError:
            tick_val = int(time.time() * 1000000)

        tick = (tick_val & 0xFFFFFFFF).to_bytes(4, "little")

        return hashlib.sha256(tick + wallet_nonce).digest()

    def _sp_wallet_nonce(self):
        """Compute a wallet-keyed nonce from the serialized PSBT.

        sha256(root_secret || fingerprint || sha256(psbt_bytes)).
        Uses psbt.serialize() (not psbt.tx.serialize()) because SP outputs may
        have None script_pubkeys before derivation, which would cause
        TransactionOutput.write_to() to crash.
        """
        import hashlib

        psbt_hash = hashlib.sha256(self.psbt.serialize()).digest()
        return hashlib.sha256(
            self.wallet.key.root.secret + self.wallet.key.fingerprint + psbt_hash
        ).digest()

    def _populate_silent_payment_outputs(self, input_privkeys, eligible):
        """Discard incoming SP fields and compute fresh ECDH shares + DLEQ proofs.

        Incoming SP data is explicitly cleared before derivation — Krux is
        canonically the sender and never trusts coordinator-supplied SP fields.
        Do NOT inherit this clearing behaviour if receive-side support is ever
        added; a future receive module must derive its own logic.
        """
        from embit.silent_payments.ecdh import (
            compute_global_ecdh_share,
            compute_global_dleq_proof,
        )

        gc.collect()

        # Discard any incoming SP fields (coordinator-supplied, potentially wrong).
        self.psbt.sp_ecdh_shares.clear()
        self.psbt.sp_dleq_proofs.clear()
        for inp in self.psbt.inputs:
            inp.sp_ecdh_shares.clear()
            inp.sp_dleq_proofs.clear()

        wallet_nonce = self._sp_wallet_nonce()

        pairs_added = self.psbt._sign_with_sp(  # pylint: disable=protected-access
            self.wallet.key.root, aux_rand=self._sp_aux_rand(wallet_nonce)
        )
        gc.collect()

        if pairs_added == 0:
            raise ValueError(
                "Silent Payment derivation failed: no ECDH shares generated"
            )

        # Strict post-sign assertion — every eligible input must carry per-input
        # SP fields. _sign_with_sp silently skips inputs whose derivation
        # matching fails; catch that here before the QR is rendered.
        scan_key_objects = {}
        for out in self.psbt.outputs:
            if out.sp_data is not None:
                scan_key_objects[out.sp_data.scan_key.sec()] = out.sp_data.scan_key
        for i in eligible:
            inp = self.psbt.inputs[i]
            missing_share = any(sk not in inp.sp_ecdh_shares for sk in scan_key_objects)
            missing_proof = any(sk not in inp.sp_dleq_proofs for sk in scan_key_objects)
            if missing_share or missing_proof:
                raise ValueError(
                    "Silent Payment signing failed: input %d is eligible but is "
                    "missing per-input ECDH share/DLEQ for one or more scan keys. "
                    "This usually indicates the BIP-32 derivation for input %d "
                    "does not derive to the public key the PSBT claims." % (i, i)
                )

        # Populate PSBT-global ECDH shares + DLEQ proofs. Coordinators such as
        # Sparrow check global fields first and skip per-input checks when they
        # are present, and the global fields survive per-input finalization.
        priv_keys = [secret for secret, _ in input_privkeys]

        if priv_keys:
            global_aux = self._sp_aux_rand(wallet_nonce)
            for sk_bytes, scan_key in scan_key_objects.items():
                global_share = compute_global_ecdh_share(priv_keys, scan_key)
                if global_share is not None:
                    global_proof = compute_global_dleq_proof(
                        priv_keys, scan_key, global_share, aux_rand=global_aux
                    )
                    self.psbt.sp_ecdh_shares[sk_bytes] = global_share
                    self.psbt.sp_dleq_proofs[sk_bytes] = global_proof

        gc.collect()

    def _validate_sp_signing_inputs(self):
        """Pre-check that inputs satisfy SP signing requirements.

        _sign_with_sp has several silent-return-0 paths. Running the same
        checks here turns each into a descriptive ValueError so the user
        (and developers) can see exactly what went wrong.

        Returns (eligible, input_privkeys): the eligible input indices and a
        (secret, is_xonly) pair per eligible input, resolved once here so
        callers do not repeat the BIP-32/EC derivation work. Resolution is
        delegated to embit's _resolve_input_privkey so every SP consumer
        (per-input ECDH share, global share and output-script derivation)
        sums the exact same secret. For taproot inputs that secret is already
        even-Y normalized per BIP-352: ordinary BIP-86 keys via the taproot
        tweak, BIP-376 spend-from inputs via the spend-key tweak. is_xonly
        marks taproot inputs so create_outputs treats them as x-only.
        """
        from embit.silent_payments.ecdh import get_eligible_inputs
        from embit.silent_payments.fields import SPValidationError

        try:
            eligible = get_eligible_inputs(self.psbt.inputs, has_sp_outputs=True)
        except SPValidationError as e:
            raise ValueError("Silent Payment signing failed: %s" % e)

        if not eligible:
            types = []
            for i, inp in enumerate(self.psbt.inputs):
                spk = inp.script_pubkey
                if spk is None:
                    types.append("input %d: no UTXO" % i)
                else:
                    types.append("input %d: %s" % (i, spk.script_type()))
            raise ValueError(
                "Silent Payment signing failed: no eligible inputs. %s"
                % "; ".join(types)
            )

        # Each eligible input must resolve to a wallet-owned private key, since
        # BIP-352 requires every eligible input to contribute to the shared
        # secret. _resolve_input_privkey handles all eligible types: non-taproot
        # via BIP-32 derivations, BIP-86 taproot via the taproot tweak, and
        # BIP-376 spend-from inputs via the spend-key tweak.
        root = self.wallet.key.root
        fingerprint = root.my_fingerprint
        input_privkeys = []
        for i in eligible:
            inp = self.psbt.inputs[i]
            # pylint: disable=protected-access
            secret = self.psbt._resolve_input_privkey(inp, root, fingerprint)
            if secret is None:
                raise ValueError(
                    "Silent Payment signing failed: input %d key could not be "
                    "derived from this wallet (check the BIP-32 / SP spend "
                    "derivation and fingerprint)" % i
                )
            is_xonly = (
                inp.script_pubkey is not None
                and inp.script_pubkey.script_type() == "p2tr"
            )
            input_privkeys.append((secret, is_xonly))

        return eligible, input_privkeys

    def _derive_sp_output_scripts(self, input_privkeys):
        """Derive P2TR scripts for SP outputs that have script_pubkey=None.

        Krux holds the input private keys, so output derivation uses the
        canonical BIP-352 sender routine (create_outputs) directly rather than
        recombining the per-input ECDH shares. Outputs that already have a
        script_pubkey are left untouched.
        """
        from embit.silent_payments import create_outputs
        from embit.transaction import COutPoint
        from embit.script import Script
        from binascii import unhexlify

        # SP outputs still awaiting their derived P2TR script, in output (vout)
        # index order. create_outputs assigns the BIP-352 derivation counter k
        # in recipient-list order within each scan-key group, and the BIP-375
        # validator re-derives k in output-index order within each scan-key
        # group — so recipients MUST be passed in output-index order for the two
        # to agree. (Sorting by spend key here would assign mismatched k values
        # to two outputs sharing a scan key, e.g. labeled addresses of the same
        # recipient, and the validator would reject the PSBT.)
        pending = [
            (i, out)
            for i, out in enumerate(self.psbt.outputs)
            if out.sp_data is not None and out.script_pubkey is None
        ]

        if not pending:
            return

        if not input_privkeys:
            return

        # Per BIP-352 the input hash mixes every transaction outpoint, so all
        # inputs contribute outpoints while only eligible inputs contribute keys.
        outpoints = [COutPoint(inp.txid, inp.vout) for inp in self.psbt.inputs]

        recipients = [
            self._silent_payment_address_from_output(out) for _, out in pending
        ]
        outputs_map = create_outputs(input_privkeys, outpoints, recipients)
        gc.collect()

        # Hand each derived P2TR back to a pending output for its address. A
        # cursor walks each address's list so repeated recipients each receive a
        # distinct derived script. The BIP-352 key P_k is the final taproot
        # output key, so the scriptPubKey is a raw "OP_1 <32-byte x-only>" — no
        # additional BIP-341 taproot tweak (which p2tr() would apply).
        cursor = {}
        for addr, (_, out) in zip(recipients, pending):
            derived = outputs_map.get(addr)
            pos = cursor.get(addr, 0)
            if not derived or pos >= len(derived):
                continue
            xonly = unhexlify(derived[pos])
            out.script_pubkey = Script(b"\x51\x20" + xonly)
            cursor[addr] = pos + 1

        # Every pending SP output must now have a script; an undelivered output
        # would otherwise reach add_signatures() with a None script and crash
        # sighash computation.
        for _, out in pending:
            if out.script_pubkey is None:
                raise ValueError(
                    "Silent Payment derivation failed: an output script could "
                    "not be derived"
                )

        gc.collect()

    def add_signatures(self):
        """Add signatures to PSBT"""
        self.check_sighash()
        # with_sp_shares=False: SP shares/proofs are populated explicitly by
        # _populate_silent_payment_outputs (with Krux aux randomness) before
        # signing, so embit's SP pass would only re-verify our own freshly
        # generated DLEQ proofs — wasted EC work on the signing hot path.
        sigs_added = self.psbt.sign_with(self.wallet.key.root, with_sp_shares=False)
        if sigs_added == 0:
            raise ValueError("cannot sign")

    def fill_zero_fingerprint(self):
        """Fix for zeroes in fingerprint that happen when user imports the wallet
        with XPUB only (without derivation path)
        """
        filled = 0

        for inp in self.psbt.inputs:
            filled += self._fill_zero_fingerprint_scope(inp)

        for out in self.psbt.outputs:
            filled += self._fill_zero_fingerprint_scope(out)

        return filled

    def _fill_zero_fingerprint_scope(self, scope):
        """Helper function to fill a scope (input/output)"""
        filled = 0
        if self.policy["type"] == P2TR:
            derivations = scope.taproot_bip32_derivations
        else:
            derivations = scope.bip32_derivations
        for pub in derivations:
            if self.policy["type"] == P2TR:
                derivation = derivations[pub][1]  # ignore taproot leaf
            else:
                derivation = derivations[pub]
            if derivation.fingerprint == b"\x00\x00\x00\x00":
                # check if pubkey matches
                if self.wallet.key.get_xpub(derivation.derivation).key == pub:
                    derivation.fingerprint = self.wallet.key.fingerprint
                    filled += 1
        return filled

    def sign(self, trim=True):
        """Signs the PSBT and preserves necessary fields for the final transaction"""
        # _has_sp is set by validate(); the trim below preserves sp_data, so
        # it also holds for the rebuilt PSBT.
        has_sp = self._has_sp
        if has_sp:
            eligible, input_privkeys = self._validate_sp_signing_inputs()

            # Populate per-input ECDH shares + DLEQ proofs with Krux entropy.
            # Incoming SP fields are discarded inside
            # _populate_silent_payment_outputs.
            self._populate_silent_payment_outputs(input_privkeys, eligible)

            # Derive P2TR output scripts for SP outputs that are still empty.
            # Coordinators omit PSBT_OUT_SCRIPT for SP outputs per BIP-375; the
            # signer must derive them before sighash computation.
            self._derive_sp_output_scripts(input_privkeys)

            self._validate_silent_payment(skip_output_scripts=False)

        self.add_signatures()

        if not trim:
            return

        # Pass version to preserve PSBTv2 when the source PSBT is v2 (SP).
        trimmed_psbt = PSBT(self.psbt.tx, version=self.psbt.version)
        for i, inp in enumerate(self.psbt.inputs):
            # Copy the final_scriptwitness if present
            if inp.final_scriptwitness:
                trimmed_psbt.inputs[i].final_scriptwitness = inp.final_scriptwitness

            # Copy any partial signatures
            if inp.partial_sigs:
                trimmed_psbt.inputs[i].partial_sigs = inp.partial_sigs

            # Preserve witness UTXO if present
            if inp.witness_utxo:
                trimmed_psbt.inputs[i].witness_utxo = inp.witness_utxo

            # Preserve non-witness UTXO if present (for legacy inputs)
            if inp.non_witness_utxo:
                trimmed_psbt.inputs[i].non_witness_utxo = inp.non_witness_utxo

            # Preserve redeem_script for P2SH or nested SegWit
            if inp.redeem_script:
                trimmed_psbt.inputs[i].redeem_script = inp.redeem_script

            # Preserve witness_script for P2WSH multisig
            if inp.witness_script:
                trimmed_psbt.inputs[i].witness_script = inp.witness_script

            # Preserve taproot_key_sig for Taproot inputs
            if inp.taproot_key_sig:
                trimmed_psbt.inputs[i].taproot_key_sig = inp.taproot_key_sig

            # Preserve taproot script path sigs
            if inp.taproot_sigs:
                trimmed_psbt.inputs[i].taproot_sigs = inp.taproot_sigs

            # Preserve BIP-375 per-input SP ECDH shares and DLEQ proofs only
            # when no global share covers them: BIP-375 requires
            # PSBT_IN_BIP32_DERIVATION alongside a per-input DLEQ proof for
            # non-taproot inputs, and the trim strips those derivations. The
            # global fields (preserved below) carry the ECDH coverage instead,
            # and dropping the per-input copies also shrinks the QR payload.
            if not self.psbt.sp_ecdh_shares:
                trimmed_psbt.inputs[i].sp_ecdh_shares = inp.sp_ecdh_shares
                trimmed_psbt.inputs[i].sp_dleq_proofs = inp.sp_dleq_proofs

        if has_sp:
            # Preserve BIP-375 global SP fields on the trimmed PSBT.
            trimmed_psbt.sp_ecdh_shares = self.psbt.sp_ecdh_shares
            trimmed_psbt.sp_dleq_proofs = self.psbt.sp_dleq_proofs

            # Preserve BIP-375 per-output SP metadata. PSBT(self.psbt.tx, …)
            # builds fresh SPOutputScopes with sp_data=None; without this loop
            # the exported PSBT omits PSBT_OUT_SP_V0_INFO and the coordinator
            # cannot tie the derived P2TR back to the SP recipient address.
            for i, out in enumerate(self.psbt.outputs):
                if out.sp_data is not None:
                    trimmed_psbt.outputs[i].sp_data = out.sp_data
                if out.sp_label is not None:
                    trimmed_psbt.outputs[i].sp_label = out.sp_label

            # Per BIP-375, once SP output scripts are set the tx is non-modifiable.
            trimmed_psbt.tx_modifiable_flags = 0

        self.psbt = trimmed_psbt

        if has_sp:
            # Re-validate the trimmed PSBT: the pre-sign check (above) covered the
            # populated PSBT; this confirms the trim/rebuild preserved every SP
            # field on the artifact that actually leaves the device.
            self._validate_silent_payment(skip_output_scripts=False)

    def psbt_qr(self):
        """Returns the psbt in the same form it was read as a QR code"""
        psbt_data = self.psbt.serialize()

        self.psbt = None  # Remove PSBT free RAM
        gc.collect()

        if self.qr_format == FORMAT_BBQR:
            from .bbqr import encode_bbqr

            psbt_data = encode_bbqr(psbt_data, file_type="P")
            return psbt_data, self.qr_format

        if self.base_encoding is not None:
            from .baseconv import base_encode

            psbt_data = base_encode(psbt_data, self.base_encoding)

        if self.ur_type == Types.CRYPTO_PSBT_TYPE:
            cbor = Types.psbt_to_cbor(psbt_data)
            del psbt_data
            gc.collect()
            return UR(Types.CRYPTO_PSBT_TYPE, cbor), self.qr_format
        return psbt_data, self.qr_format

    def xpubs(self):
        """Returns the xpubs in the PSBT mapped to their derivations, falling back to
        the wallet descriptor xpubs if not found
        """
        from embit.psbt import DerivationPath

        if self.psbt.xpubs:
            return self.psbt.xpubs, None

        if not self.wallet.descriptor:
            raise ValueError("missing xpubs")

        descriptor_keys = (
            self.wallet.descriptor.keys
            if self.wallet.descriptor.keys
            else [self.wallet.descriptor.key]
        )
        xpubs = {}
        origin_less_xpub = None
        for descriptor_key in descriptor_keys:
            if descriptor_key.origin:
                # Pure xpub descriptors (Blue Wallet) don't have origin data
                xpubs[descriptor_key.key] = DerivationPath(
                    descriptor_key.origin.fingerprint, descriptor_key.origin.derivation
                )
            elif len(descriptor_keys) > 1:
                # Allow one descriptor key without origin data for taproot
                # Pure taptree descriptors won't have origin data for internal key.
                # Reject more than one origin-less key in a multi-key descriptor:
                # otherwise unverifiable cosigners would be silently accepted.
                if origin_less_xpub is not None:
                    raise ValueError(
                        "multiple xpubs without origin in multi-key descriptor"
                    )
                origin_less_xpub = descriptor_key.key

        return xpubs, origin_less_xpub

    def psbt_policy_string(self):
        """Returns the policy string containing script type and cosigners' fingerprints"""

        policy_str = "PSBT policy:\n"
        policy_str += self.policy["type"] + "\n"
        if is_multisig(self.policy):
            policy_str += str(self.policy["m"]) + " of " + str(self.policy["n"]) + "\n"
        fingerprints = []
        for inp in self.psbt.inputs:
            # Do we need to loop through all the inputs or just one?
            if self.policy["type"] == P2WSH:
                for pub in inp.bip32_derivations:
                    fingerprint_srt = Key.format_fingerprint(
                        inp.bip32_derivations[pub].fingerprint, True
                    )
                    if fingerprint_srt not in fingerprints:
                        if len(fingerprints) > MAX_POLICY_COSIGNERS_DISPLAYED:
                            fingerprints[-1] = ELLIPSIS
                            break
                        fingerprints.append(fingerprint_srt)
            elif self.policy["type"] == P2TR:
                for pub in inp.taproot_bip32_derivations:
                    _, derivation_path = inp.taproot_bip32_derivations[pub]
                    fingerprint_srt = Key.format_fingerprint(
                        derivation_path.fingerprint, True
                    )
                    if fingerprint_srt not in fingerprints:
                        if len(fingerprints) > MAX_POLICY_COSIGNERS_DISPLAYED:
                            fingerprints[-1] = ELLIPSIS
                            break
                        fingerprints.append(fingerprint_srt)

        policy_str += "\n".join(fingerprints)
        return policy_str


def is_multisig(policy):
    """Returns a boolean indicating if the policy is a multisig"""
    return (
        "type" in policy
        and policy["type"] in (P2SH, P2SH_P2WSH, P2WSH)
        and "m" in policy
        and "n" in policy
        # and "cosigners" in policy
    )


def is_miniscript(policy):
    """Returns a boolean indicating if the policy is a miniscript"""
    # m and n will not be present in miniscript policies
    return (
        "type" in policy
        and policy["type"] in (P2WSH, P2TR)
        and "miniscript" in policy
        and "m" not in policy
        and "n" not in policy
    )


# From: https://github.com/diybitcoinhardware/embit/blob/master/examples/change.py#L41
def get_cosigners(pubkeys, derivations, xpubs):
    """Returns xpubs used to derive pubkeys using global xpub field from psbt"""
    cosigners = []
    for _, pubkey in enumerate(pubkeys):
        if pubkey not in derivations:
            raise ValueError("missing derivation")
        der = derivations[pubkey]
        for xpub in xpubs:
            origin_der = xpubs[xpub]
            # check fingerprint
            if origin_der.fingerprint == der.fingerprint:
                # check derivation - last two indexes give pub from xpub
                if origin_der.derivation == der.derivation[:-2]:
                    # check that it derives to pubkey actually
                    if xpub.derive(der.derivation[-2:]).key == pubkey:
                        # append strings so they can be sorted and compared
                        cosigners.append(xpub.to_base58())
                        break
    if len(cosigners) != len(pubkeys):
        raise ValueError("cannot get all cosigners")
    return sorted(cosigners)


def get_cosigners_miniscript(derivations, xpubs):
    """Compares the derivations with the xpubs to check and get the cosigners"""
    cosigners = []
    for pubkey, der in derivations.items():
        for xpub in xpubs:
            origin_der = xpubs[xpub]
            # Check that the fingerprint matches
            if origin_der.fingerprint == der.fingerprint:
                # Check that the derivation path matches except for the last two indices
                if origin_der.derivation == der.derivation[:-2]:
                    # Verify that the xpub derives the pubkey
                    if xpub.derive(der.derivation[-2:]).key == pubkey:
                        # Append the xpub as a base58 string
                        cosigners.append(xpub.to_base58())
                        break
    # Ensure all pubkeys have a matching xpub
    if len(cosigners) != len(derivations):
        raise ValueError("cannot get all cosigners")
    return sorted(cosigners)


def get_cosigners_taproot_miniscript(taproot_derivations, xpubs, origin_less_xpub=None):
    """
    Compares the taproot derivations with the xpubs to check get the cosigners
    """

    cosigners = []
    for xonly_pubkey, der_info in taproot_derivations.items():
        _, der = der_info  # tap_leaf_hashes are not used
        fp = der.fingerprint
        full_path = der.derivation

        for xpub in xpubs:
            origin_der = xpubs[xpub]
            # Check that the fingerprint matches
            if origin_der.fingerprint == fp:
                # Check that the origin derivation is a prefix of the full derivation path
                if full_path[: len(origin_der.derivation)] == origin_der.derivation:
                    # Derive the remainder of the path
                    remainder = full_path[len(origin_der.derivation) :]
                    # Verify that the xpub derives to the given xonly_pubkey
                    derived_key = xpub.derive(remainder).key
                    if derived_key.xonly() == xonly_pubkey.xonly():
                        # Append the xpub as a base58 string
                        cosigners.append(xpub.to_base58())
                        break

    if origin_less_xpub:
        # Pocicies which don't cover internal key spending (e.g. taptree only)
        # can have an origin-less xpub for internal key derivation
        cosigners.append(origin_less_xpub.to_base58())

    # Ensure all pubkeys have a matching xpub
    if len(cosigners) != len(taproot_derivations):
        raise ValueError("cannot get all cosigners")

    return sorted(cosigners)


# Modified from: https://github.com/diybitcoinhardware/embit/blob/master/examples/change.py#L64
# and https://github.com/SeedSigner/seedsigner/blob/dev/src/seedsigner/models/psbt_parser.py
def get_policy(scope, scriptpubkey, xpubs, origin_less_xpub=None):
    """Parse scope and get policy"""
    from embit.finalizer import parse_multisig

    # we don't know the policy yet, let's parse it
    script_type = scriptpubkey.script_type()

    # p2sh can be either:
    # - legacy multisig (p2sh);
    # - nested segwit singlesig (p2sh-p2wpkh);
    # - nested segwit multisig (p2sh-p2wsh).
    if script_type == P2SH:
        if scope.witness_script is not None:
            script_type = P2SH_P2WSH
        elif (
            scope.redeem_script is not None
            and scope.redeem_script.script_type() == P2WPKH
        ):
            script_type = P2SH_P2WPKH

    policy = {"type": script_type}

    if P2SH == script_type:
        try:
            # Try to parse as multisig
            if scope.redeem_script is None:
                raise ValueError("Missing redeem script")
            m, pubkeys = parse_multisig(scope.redeem_script)
            policy.update({"m": m, "n": len(pubkeys)})

            # check pubkeys are derived from cosigners
            cosigners = get_cosigners(pubkeys, scope.bip32_derivations, xpubs)
            policy.update({"cosigners": cosigners})
        except:
            pass

    if P2WSH in script_type:
        try:
            # Try to parse as multisig
            if scope.witness_script is None:
                raise ValueError("Missing witness script")

            m, pubkeys = parse_multisig(scope.witness_script)
            policy.update({"m": m, "n": len(pubkeys)})

            # check pubkeys are derived from cosigners
            cosigners = get_cosigners(pubkeys, scope.bip32_derivations, xpubs)
            policy.update({"cosigners": cosigners})
        except:
            try:
                # Try to parse as miniscript
                policy.update({"miniscript": P2WSH})

                # Will succeed to verify cosigners only if the descriptor is loaded
                cosigners = get_cosigners_miniscript(scope.bip32_derivations, xpubs)
                policy.update({"cosigners": cosigners})
            except:
                pass

    if script_type == P2TR:
        try:
            # Try to parse as taproot miniscript
            if len(scope.taproot_bip32_derivations) > 1:

                # Assume is miniscript if there are multiple cosigners
                policy.update({"miniscript": P2TR})

            # Will succeed to verify cosigners only if the descriptor is loaded
            cosigners = get_cosigners_taproot_miniscript(
                scope.taproot_bip32_derivations, xpubs, origin_less_xpub
            )
            # Only add cosigners if is miniscript (multiple cosigners),
            # otherwise it probably is single-sig taproot
            if len(cosigners) > 1:
                policy.update({"cosigners": cosigners})
        except:
            pass

    return policy
