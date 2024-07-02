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

from .key import P2PKH, P2SH, P2SH_P2WPKH, P2SH_P2WSH, P2WPKH, P2WSH, P2TR


class SatsVB:
    """Responsible for validating and signing PSBTs"""

    # Consts to calculate fees/vB:
    P2PKH_IN_SIZE = 148
    P2PKH_OUT_SIZE = 34
    P2SH_OUT_SIZE = P2SH_P2WPKH_OUT_SIZE = P2SH_P2WSH_OUT_SIZE = 32

    # All segwit input sizes are reduced by 1 WU to account for the witness item
    # counts being added for every input per the transaction header
    P2SH_P2WPKH_IN_SIZE = 90.75

    P2WPKH_IN_SIZE = 67.75
    P2WPKH_OUT_SIZE = 31
    P2WSH_OUT_SIZE = P2TR_OUT_SIZE = 43
    P2TR_IN_SIZE = 57.25

    PUBKEY_SIZE = 33
    SIGNATURE_SIZE = 72

    ONE_BYTE_MAX_SIZE = 0xFF
    TWO_BYTE_MAX_SIZE = 0xFFFF
    FOUR_BYTE_MAX_SIZE = 0xFFFFFFFF

    TX_HEADER_VERSION_SIZE = TX_HEADER_LOCKTIME_SIZE = TX_INPUT_VOUT_SIZE = (
        TX_INPUT_SEQUENCE_SIZE
    ) = 4
    TX_INPUT_TXID_SIZE = 32
    TX_SEGWIT_INPUT_MARKER = TX_SEGWIT_INPUT_FLAG = TX_SEGWIT_INPUT_DISCOUNT = 0.25

    @classmethod
    def _get_size_of_script_length_element(cls, length):
        """Get size of script in bytes for fees/vB"""
        if length < 75:
            return 1
        if length <= cls.ONE_BYTE_MAX_SIZE:
            return 2
        if length <= cls.TWO_BYTE_MAX_SIZE:
            return 3
        return 5

    @classmethod
    def _get_size_of_var_int(cls, length):
        """Get size of int in bytes for fees/vB"""
        if length < 253:
            return 1
        if length < cls.TWO_BYTE_MAX_SIZE:
            return 3
        if length < cls.FOUR_BYTE_MAX_SIZE:
            return 5
        return 9

    @classmethod
    def _get_tx_overhead_vbytes(cls, input_script, input_count, output_count):
        """Get tx size overhead in bytes for fees/vB."""
        return (
            cls.TX_HEADER_VERSION_SIZE  # nVersion
            + cls._get_size_of_var_int(input_count)  # number of inputs
            + cls._get_size_of_var_int(output_count)  # number of outputs
            + cls.TX_HEADER_LOCKTIME_SIZE  # nLockTime
            + cls._get_witness_bytes(input_script, input_count)
        )

    @classmethod
    def _get_witness_bytes(cls, input_script, input_count):
        """Get witness bytes for fees/vB. We do not allow mixed inputs in the PSBT,
        otherwise this would need to be revised"""
        if input_script in (P2PKH, P2SH):
            return 0

        # Transactions with segwit inputs have extra overhead
        return (
            cls.TX_SEGWIT_INPUT_MARKER  # segwit marker
            + cls.TX_SEGWIT_INPUT_FLAG  # segwit flag
            + input_count
            * cls.TX_SEGWIT_INPUT_DISCOUNT  # witness element count per input
        )

    @classmethod
    def _get_redeem_script_size(cls, policy):
        """Get Redeem script in bytes for fees/vB"""
        return (
            1
            + policy["n"] * (1 + cls.PUBKEY_SIZE)  # OP_M
            + 1  # OP_PUSH33 <pubkey>
            + 1  # OP_N  # OP_CHECKMULTISIG
        )

    @classmethod
    def _get_script_signature_size(cls, policy, redeem_script_size):
        """Get Script signature size for fees/vB"""
        return (
            1
            + policy["m"] * (1 + cls.SIGNATURE_SIZE)  # size(0)
            + cls._get_size_of_script_length_element(  # size(SIGNATURE_SIZE) + signature
                redeem_script_size
            )
            + redeem_script_size
        )

    @classmethod
    def get_vbytes(cls, policy, output_policy_count, input_count, output_count):
        """Get PSBT virtual bytes (vB)"""
        # In most cases the input size is predictable.
        # For multisig inputs we need to perform a detailed calculation
        input_size = 0  # in virtual bytes

        # We do not allow mixed inputs in the PSBT,
        # otherwise we would need to add size for each input policy
        if policy["type"] == P2PKH:
            input_size += cls.P2PKH_IN_SIZE
        elif policy["type"] == P2SH_P2WPKH:
            input_size += cls.P2SH_P2WPKH_IN_SIZE
        elif policy["type"] == P2WPKH:
            input_size += cls.P2WPKH_IN_SIZE

        # Only consider the cooperative taproot signing path;
        # assume multisig is done via aggregate signatures
        elif policy["type"] == P2TR:
            input_size += cls.P2TR_IN_SIZE
        elif policy["type"] == P2SH:
            redeem_script_size = cls._get_redeem_script_size(policy)
            script_sig_size = cls._get_script_signature_size(policy, redeem_script_size)
            input_size += (
                cls.TX_INPUT_TXID_SIZE
                + cls.TX_INPUT_VOUT_SIZE
                + cls._get_size_of_var_int(script_sig_size)
                + script_sig_size
                + cls.TX_INPUT_SEQUENCE_SIZE
            )
        elif policy["type"] in (P2SH_P2WSH, P2WSH):
            redeem_script_size = cls._get_redeem_script_size(policy)
            input_witness_size = cls._get_script_signature_size(
                policy, redeem_script_size
            )
            input_size += (
                cls.TX_INPUT_TXID_SIZE
                + cls.TX_INPUT_VOUT_SIZE
                + input_witness_size
                * cls.TX_SEGWIT_INPUT_DISCOUNT  # outpoint (spent UTXO ID)
                + cls.TX_INPUT_SEQUENCE_SIZE  # witness program  # nSequence
            )
            if policy["type"] == P2SH_P2WSH:
                input_size += cls.TX_INPUT_TXID_SIZE + 3
                # P2SH wrapper (redeemscript hash) + overhead?

        policy_size = 0
        for policy_type, v in output_policy_count.items():
            if policy_type == P2PKH:
                policy_size += cls.P2PKH_OUT_SIZE * v
            elif policy_type == P2SH:
                policy_size += cls.P2SH_OUT_SIZE * v
            elif policy_type == P2SH_P2WPKH:
                policy_size += cls.P2SH_P2WPKH_OUT_SIZE * v
            elif policy_type == P2SH_P2WSH:
                policy_size += cls.P2SH_P2WSH_OUT_SIZE * v
            elif policy_type == P2WPKH:
                policy_size += cls.P2WPKH_OUT_SIZE * v
            elif policy_type == P2WSH:
                policy_size += cls.P2WSH_OUT_SIZE * v
            elif policy_type == P2TR:
                policy_size += cls.P2TR_OUT_SIZE * v

        vbytes = (
            cls._get_tx_overhead_vbytes(policy["type"], input_count, output_count)
            # We do not allow mixed inputs in the PSBT,
            # otherwise we would not multiply here by input_count
            + input_size * input_count
            + policy_size
        )

        import math

        return math.ceil(vbytes)
