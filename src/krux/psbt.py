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
from embit.psbt import PSBT
from embit.bip32 import HARDENED_INDEX
from ur.ur import UR
import urtypes
from urtypes.crypto import CRYPTO_PSBT
from .baseconv import base_decode
from .krux_settings import t
from .settings import THIN_SPACE
from .qr import FORMAT_PMOFN, FORMAT_BBQR
from .key import Key, P2PKH, P2SH, P2SH_P2WPKH, P2SH_P2WSH, P2WPKH, P2WSH, P2TR
from .sats_vb import SatsVB

# PSBT Output Types:
CHANGE = 0
SELF_TRANSFER = 1
SPEND = 2

# We always uses thin spaces after the ₿ in this file
BTC_SYMBOL = "₿"


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

        # Parse the PSBT
        if psbt_filename:
            gc.collect()
            from .sd_card import SD_PATH

            file_path = "/%s/%s" % (SD_PATH, psbt_filename)
            try:
                with open(file_path, "rb") as file:
                    self.psbt = PSBT.read_from(file, compress=1)
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
                        # Legacy will fail to get policy from compressed PSBT
                        # so we load it uncompressed
                        with open(file_path, "rb") as file:
                            file.seek(0)  # Reset the file pointer to the beginning
                            self.psbt = PSBT.read_from(file)
                except Exception as e:
                    raise ValueError("Error loading PSBT file: %s" % e)
            self.base_encoding = 64  # In case it is exported as QR code
        elif isinstance(psbt_data, UR):
            try:
                self.psbt = PSBT.parse(
                    urtypes.crypto.PSBT.from_cbor(psbt_data.cbor).data
                )
                self.ur_type = CRYPTO_PSBT
                # self.base_encoding = 64
            except:
                raise ValueError("invalid PSBT")
        else:
            # Process as bytes
            psbt_data = psbt_data.encode() if isinstance(psbt_data, str) else psbt_data
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
                            self.psbt = PSBT.parse(base_decode(psbt_data, 43))
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
                base_decode(chunk, 64)
                return True
            except Exception:
                return False

    def validate(self):
        """Validates the PSBT"""
        # From: https://github.com/diybitcoinhardware/embit/blob/master/examples/change.py#L110
        xpubs = []
        try:
            xpubs = self.xpubs()
        except:
            # Expected to fail to get xpubs from Miniscript PSBT
            pass
        for inp in self.psbt.inputs:
            # get policy of the input
            try:
                inp_policy = self.get_policy_from_psbt_input(inp, xpubs)
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

    def get_policy_from_psbt_input(self, tx_input, xpubs):
        """Extracts the scriptPubKey from an input's UTXO and determines the policy."""
        if tx_input.witness_utxo:
            scriptpubkey = tx_input.witness_utxo.script_pubkey
        elif tx_input.non_witness_utxo:
            # Retrieve the scriptPubKey from the specified output in the non_witness_utxo
            scriptpubkey = tx_input.non_witness_utxo.vout[tx_input.vout].script_pubkey
        else:
            raise ValueError("No UTXO information available in the input.")

        return get_policy(tx_input, scriptpubkey, xpubs)

    def path_mismatch(self):
        """Verifies if the PSBT path matches wallet's derivation path"""
        mismatched_paths = []
        der_path_nodes = len(self.wallet.key.derivation.split("/")) - 1
        for _input in self.psbt.inputs:
            if self.policy["type"] == P2TR:
                derivations = _input.taproot_bip32_derivations
            else:
                derivations = _input.bip32_derivations
            for pubkey in derivations:
                if self.policy["type"] == P2TR:
                    derivation_path = derivations[pubkey][
                        1
                    ].derivation  # ignore taproot leaf
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

    def is_our_miniscript_output(self, psbt_output):
        """Check if the output is from our wallet"""

        # TODO: Is comparing fingerprints and paths a trustable method?
        derivations = psbt_output.bip32_derivations
        if not derivations:
            return False
        for _, derivation in derivations.items():
            # Check if the fingerprint matches
            if derivation.fingerprint == self.wallet.key.fingerprint:
                # Verify the derivation path
                expected_path_str = self.wallet.key.derivation.split("/")[1:]
                expected_path_nodes = []
                for p in expected_path_str:
                    if "h" in p:
                        expected_path_nodes.append(int(p[:-1]) + HARDENED_INDEX)
                    else:
                        expected_path_nodes.append(int(p))

                if derivation.derivation[:4] == expected_path_nodes:
                    return True
        return False

    def _classify_output(self, out_policy, i, out):
        """Classify the output based on its properties and policy"""
        from embit import script

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

            # empty script by default
            sc = script.Script(b"")
            if self.policy["type"] == P2WSH:
                try:
                    # if multisig, we know witness script
                    sc = script.p2wsh(out.witness_script)
                except:
                    # Expected to fail with Miniscript PSBT
                    pass
            elif self.policy["type"] == P2SH_P2WSH:
                sc = script.p2sh(script.p2wsh(out.witness_script))
            # single-sig
            elif "pkh" in self.policy["type"]:
                if len(list(out.bip32_derivations.values())) > 0:
                    der = list(out.bip32_derivations.values())[0].derivation
                    my_hd_prvkey = self.wallet.key.root.derive(der)
                    if self.policy["type"] == P2WPKH:
                        sc = script.p2wpkh(my_hd_prvkey)
                    elif self.policy["type"] == P2SH_P2WPKH:
                        sc = script.p2sh(script.p2wpkh(my_hd_prvkey))
                    elif self.policy["type"] == P2PKH:
                        sc = script.p2pkh(my_hd_prvkey)

            if self.policy["type"] == P2TR:
                address_from_my_wallet = (
                    len(list(out.taproot_bip32_derivations.values())) > 0
                )
                if address_from_my_wallet:
                    # _ = leafs
                    _, der = list(out.taproot_bip32_derivations.values())[0]
                    address_is_change = der.derivation[3] == 1
            else:
                if sc.data:
                    address_from_my_wallet = (
                        sc.data == self.psbt.tx.vout[i].script_pubkey.data
                    )
                else:
                    # If the script is empty, we compare fingerprints and paths
                    address_from_my_wallet = self.is_our_miniscript_output(out)
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

    def outputs(self):
        """Returns a list of messages describing where amounts are going"""
        from .format import format_btc, replace_decimal_separator

        inp_amount = 0
        for inp in self.psbt.inputs:
            if inp.witness_utxo:
                inp_amount += inp.witness_utxo.value
            elif inp.non_witness_utxo:  # Legacy
                # Retrieve the value from the specified output in the non_witness_utxo
                inp_amount += inp.non_witness_utxo.vout[inp.vout].value
        resume_inputs_str = (
            (t("Inputs (%d):") % len(self.psbt.inputs))
            + (" " + BTC_SYMBOL + THIN_SPACE + "%s" % format_btc(inp_amount))
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
        try:
            xpubs = self.xpubs()
        except:
            # Expected to fail to get xpubs from Miniscript PSBT
            pass
        for i, out in enumerate(self.psbt.outputs):
            out_policy = get_policy(out, self.psbt.tx.vout[i].script_pubkey, xpubs)
            output_policy_count[out_policy["type"]] += 1
            output_type = self._classify_output(out_policy, i, out)

            if output_type == CHANGE:
                change_list.append(
                    (
                        self.psbt.tx.vout[i].script_pubkey.address(
                            network=self.wallet.key.network
                        ),
                        self.psbt.tx.vout[i].value,
                    )
                )
                change_amount += self.psbt.tx.vout[i].value
            elif output_type == SELF_TRANSFER:
                self_transfer_list.append(
                    (
                        self.psbt.tx.vout[i].script_pubkey.address(
                            network=self.wallet.key.network
                        ),
                        self.psbt.tx.vout[i].value,
                    )
                )
                self_amount += self.psbt.tx.vout[i].value
            else:  # Address is from other wallet
                spend_list.append(
                    (
                        self.psbt.tx.vout[i].script_pubkey.address(
                            network=self.wallet.key.network
                        ),
                        self.psbt.tx.vout[i].value,
                    )
                )
                spend_amount += self.psbt.tx.vout[i].value

        if len(spend_list) > 0:
            resume_spend_str = (
                (t("Spend (%d):") % len(spend_list))
                + (" " + BTC_SYMBOL + THIN_SPACE + "%s" % format_btc(spend_amount))
                + "\n\n"
            )

        if len(self_transfer_list) + len(change_list) > 0:
            resume_self_or_change_str = (
                (
                    t("Self-transfer or Change (%d):")
                    % (len(self_transfer_list) + len(change_list))
                )
                + (
                    " "
                    + BTC_SYMBOL
                    + THIN_SPACE
                    + "%s" % format_btc(self_amount + change_amount)
                )
                + "\n\n"
            )
        fee = inp_amount - spend_amount - self_amount - change_amount
        if not self.wallet.is_miniscript():
            # TODO: Tadeu - Add miniscript support to SatsVB
            satvb = fee / SatsVB.get_vbytes(
                self.policy,
                output_policy_count,
                len(self.psbt.inputs),
                len(self.psbt.outputs),
            )
        else:
            satvb = 0

        # fee percent with 1 decimal precision using math.ceil (minimum of 0.1)
        fee_percent = max(
            0.1,
            (((fee * 10000 // (spend_amount + self_amount + change_amount)) + 9) // 10)
            / 10,
        )

        resume_fee_str = (
            t("Fee:")
            + (" " + BTC_SYMBOL + THIN_SPACE + "%s" % format_btc(fee))
            + " ("
            + replace_decimal_separator("%.1f" % fee_percent)
            + "%)"
        )
        if satvb > 0:
            resume_fee_str += (" ~%.1f" % satvb) + " sat/vB"

        messages = []
        # first screen - resume
        messages.append(
            resume_inputs_str
            + resume_spend_str
            + resume_self_or_change_str
            + resume_fee_str
        )

        # sequence of spend
        for i, out in enumerate(spend_list):
            messages.append(
                (("%d. " + t("Spend:") + " \n\n%s\n\n") % (i + 1, out[0]))
                + (BTC_SYMBOL + THIN_SPACE + "%s" % format_btc(out[1]))
            )

        # sequence of self_transfer
        for i, out in enumerate(self_transfer_list):
            messages.append(
                (("%d. " + t("Self-transfer:") + " \n\n%s\n\n") % (i + 1, out[0]))
                + (BTC_SYMBOL + THIN_SPACE + "%s" % format_btc(out[1]))
            )

        # sequence of change
        for i, out in enumerate(change_list):
            messages.append(
                (("%d. " + t("Change:") + " \n\n%s\n\n") % (i + 1, out[0]))
                + (BTC_SYMBOL + THIN_SPACE + "%s" % format_btc(out[1]))
            )

        return messages, fee_percent

    def add_signatures(self):
        """Add signatures to PSBT"""
        sigs_added = self.psbt.sign_with(self.wallet.key.root)
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

    def sign(self):
        """Signs the PSBT removing all irrelevant data"""
        self.add_signatures()

        trimmed_psbt = PSBT(self.psbt.tx)
        for i, inp in enumerate(self.psbt.inputs):
            # Copy the final_scriptwitness if it's present (Taproot case)
            if inp.final_scriptwitness:
                trimmed_psbt.inputs[i].final_scriptwitness = inp.final_scriptwitness
            # Copy partial signatures for multisig or other script types
            if inp.partial_sigs:
                trimmed_psbt.inputs[i].partial_sigs = inp.partial_sigs

            # Include the PSBT_IN_WITNESS_UTXO field if it exists
            if hasattr(inp, "witness_utxo"):
                trimmed_psbt.inputs[i].witness_utxo = inp.witness_utxo

            # Include the PSBT_IN_NON_WITNESS_UTXO field if it exists (Legacy)
            if hasattr(inp, "non_witness_utxo"):
                trimmed_psbt.inputs[i].non_witness_utxo = inp.non_witness_utxo

            # Check for P2SH (Nested SegWit) and copy redeem_script if present
            if hasattr(inp, "redeem_script"):
                trimmed_psbt.inputs[i].redeem_script = inp.redeem_script

            # Check for P2WSH (SegWit multisig) and copy witness_script if present
            if hasattr(inp, "witness_script"):
                trimmed_psbt.inputs[i].witness_script = inp.witness_script

        self.psbt = trimmed_psbt

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

            psbt_data = base_encode(psbt_data, self.base_encoding).decode()

        if self.ur_type == CRYPTO_PSBT:
            return (
                UR(
                    CRYPTO_PSBT.type,
                    urtypes.crypto.PSBT(psbt_data).to_cbor(),
                ),
                self.qr_format,
            )
        return psbt_data, self.qr_format

    def xpubs(self):
        """Returns the xpubs in the PSBT mapped to their derivations, falling back to
        the wallet descriptor xpubs if not found
        """
        from embit.psbt import DerivationPath

        if self.psbt.xpubs:
            return self.psbt.xpubs

        if not self.wallet.descriptor:
            raise ValueError("missing xpubs")

        descriptor_keys = (
            [self.wallet.descriptor.key]
            if self.wallet.descriptor.key
            else self.wallet.descriptor.keys
        )
        xpubs = {}
        for descriptor_key in descriptor_keys:
            if descriptor_key.origin:
                # Pure xpub descriptors (Blue Wallet) don't have origin data
                xpubs[descriptor_key.key] = DerivationPath(
                    descriptor_key.origin.fingerprint, descriptor_key.origin.derivation
                )
        return xpubs


def is_multisig(policy):
    """Returns a boolean indicating if the policy is a multisig"""
    return (
        "type" in policy
        and P2WSH in policy["type"]
        and "m" in policy
        and "n" in policy
        # and "cosigners" in policy
    )


def is_miniscript(policy):
    """Returns a boolean indicating if the policy is a miniscript"""
    # m and n will not be present in miniscript policies
    return (
        "type" in policy
        and P2WSH in policy["type"]
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
    """Returns xpubs used to derive pubkeys listed in derivations."""
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
        raise ValueError("Not all pubkeys in derivations have corresponding xpubs")
    return sorted(cosigners)


# Modified from: https://github.com/diybitcoinhardware/embit/blob/master/examples/change.py#L64
def get_policy(scope, scriptpubkey, xpubs):
    """Parse scope and get policy"""
    from embit.finalizer import parse_multisig

    # we don't know the policy yet, let's parse it
    script_type = scriptpubkey.script_type()
    # p2sh can be either legacy multisig, or nested segwit multisig
    # or nested segwit singlesig
    if script_type == P2SH:
        if scope.witness_script is not None:
            script_type = P2SH_P2WSH
        elif (
            scope.redeem_script is not None
            and scope.redeem_script.script_type() == P2WPKH
        ):
            script_type = P2SH_P2WPKH
    policy = {"type": script_type}
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
                # Will succeed to verify cosigners only if the descriptor is loaded
                cosigners = get_cosigners_miniscript(scope.bip32_derivations, xpubs)
                policy.update({"cosigners": cosigners})
            except:
                pass
    return policy
