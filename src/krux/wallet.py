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

from embit.descriptor.descriptor import Descriptor
from embit.descriptor.arguments import Key
from embit.networks import NETWORKS
from .krux_settings import t
from .qr import FORMAT_BBQR, FORMAT_NONE
from .key import (
    P2PKH,
    P2SH,
    P2SH_P2WPKH,
    P2SH_P2WSH,
    P2WPKH,
    P2WSH,
    P2TR,
    TYPE_SINGLESIG,
    TYPE_MULTISIG,
    TYPE_MINISCRIPT,
)


class PolicyMismatchWarning(Exception):
    """An exception for wallet policy type mismatches that require user acceptance"""


class Wallet:
    """Represents the wallet that the current key belongs to"""

    def __init__(self, key):
        self.key = key
        self.wallet_data = None
        self.wallet_qr_format = FORMAT_NONE
        self.descriptor = None
        self.label = None
        self.policy = None
        self.persisted = False
        self._network = None
        if self.key and self.key.policy_type == TYPE_SINGLESIG:
            if self.key.script_type == P2PKH:
                self.descriptor = Descriptor.from_string(
                    "pkh(%s/<0;1>/*)" % self.key.key_expression()
                )
            elif self.key.script_type == P2SH_P2WPKH:
                self.descriptor = Descriptor.from_string(
                    "sh(wpkh(%s/<0;1>/*))" % self.key.key_expression()
                )
            elif self.key.script_type == P2WPKH:
                self.descriptor = Descriptor.from_string(
                    "wpkh(%s/<0;1>/*)" % self.key.key_expression()
                )

            elif self.key.script_type == P2TR:
                self.descriptor = Descriptor.from_string(
                    "tr(%s/<0;1>/*)" % self.key.key_expression()
                )
            self.label = t("Single-sig")
            self.policy = {"type": self.get_scriptpubkey_type()}

    def get_scriptpubkey_type(self):
        """Returns the scriptpubkey type of the wallet descriptor"""
        # Determine if P2SH, P2SH_P2WPKH or P2SH-P2WSH
        # This is a workaround for embit while it not
        # provides this directly
        _type = self.descriptor.scriptpubkey_type()
        if _type == P2SH:
            if self.descriptor.wpkh:
                _type = P2SH_P2WPKH
            if self.descriptor.wsh:
                _type = P2SH_P2WSH
        return _type

    def which_network(self):
        """Returns network (NETWORKS.keys()) using current wallet key, else from descriptor"""
        if self._network is None:
            if self.key:
                self._network = [
                    k for k, v in NETWORKS.items() if v == self.key.network
                ][0]
            else:
                # use first key; restrict networks to "main" and "test", version to pubkeys
                version = self.descriptor.keys[0].key.version
                for em_network in ("main", "test"):
                    for em_vertype in ("xpub", "ypub", "zpub", "Ypub", "Zpub"):
                        if version == NETWORKS[em_network][em_vertype]:
                            self._network = em_network
                            break
        return self._network

    def is_multisig(self):
        """Returns a boolean indicating whether or not the wallet is multisig"""
        if self.key:
            return self.key.policy_type == TYPE_MULTISIG
        if self.descriptor:
            return self.descriptor.is_basic_multisig
        return False

    def is_miniscript(self):
        """Returns a boolean indicating whether or not the wallet is miniscript"""
        if self.key:
            return self.key.policy_type == TYPE_MINISCRIPT
        if self.descriptor:
            if self.descriptor.is_basic_multisig:
                return False
            return (
                self.descriptor.miniscript is not None
                or self.descriptor.taptree  #  taptree is "" when not present
            )
        return False

    def is_loaded(self):
        """Returns a boolean indicating whether or not this wallet has been loaded"""
        return self.wallet_data is not None

    def _determine_descriptor_policy(self, descriptor):
        """Returns required policy type and script type from descriptor"""
        descriptor_is_multisig = descriptor.is_basic_multisig
        descriptor_is_miniscript = not descriptor_is_multisig and (
            descriptor.miniscript is not None or descriptor.taptree
        )
        descriptor_is_singlesig = (
            not descriptor_is_multisig
            and not descriptor_is_miniscript
            and descriptor.key is not None
        )

        if descriptor_is_multisig:
            return TYPE_MULTISIG, None
        if descriptor_is_miniscript:
            script_type = P2TR if descriptor.taptree else P2WSH
            return TYPE_MINISCRIPT, script_type
        if descriptor_is_singlesig or (
            not descriptor.key and len(descriptor.keys) == 1
        ):
            script_type = descriptor.scriptpubkey_type()
            # Check for nested segwit (sh(wpkh(...)))
            if script_type == "p2sh" and hasattr(descriptor, "witness_script"):
                if descriptor.witness_script:
                    # It's sh(wpkh(...)) = P2SH-P2WPKH
                    script_type = P2SH_P2WPKH
            return TYPE_SINGLESIG, script_type

        raise ValueError("Unable to determine descriptor policy type")

    def _determine_descriptor_network(self, descriptor):
        """Returns the network from descriptor's xpub version"""
        version = descriptor.keys[0].key.version
        for em_network in ("main", "test"):
            for em_vertype in ("xpub", "ypub", "zpub", "Ypub", "Zpub"):
                if version == NETWORKS[em_network][em_vertype]:
                    return NETWORKS[em_network]
        return None

    def _validate_xpub_match(self, descriptor, descriptor_xpubs):
        """Validates that key's xpub matches the descriptor"""
        if self.is_multisig():
            if not descriptor.is_basic_multisig:
                raise ValueError("not multisig")
            if self.key.xpub() not in descriptor_xpubs:
                raise ValueError("xpub not a multisig cosigner")
        elif self.is_miniscript():
            if self.key.script_type == P2WSH:
                if descriptor.miniscript is None or descriptor.is_basic_multisig:
                    raise ValueError("not P2WSH miniscript")
            elif self.key.script_type == P2TR:
                if not descriptor.taptree:
                    raise ValueError("not P2TR miniscript")
            if self.key.xpub() not in descriptor_xpubs:
                raise ValueError("xpub not a miniscript cosigner")
        else:
            if not descriptor.key and len(descriptor.keys) > 1:
                raise ValueError("not single-sig")
            if self.key.xpub() != descriptor_xpubs[0]:
                raise ValueError("xpub does not match")

    def _validate_descriptor(self, descriptor, descriptor_xpubs):
        """Validates the descriptor against the current key and policy type"""
        # Determine required policy and script type from descriptor
        required_policy_type, required_script_type = self._determine_descriptor_policy(
            descriptor
        )

        # Determine required network from descriptor
        required_network = self._determine_descriptor_network(descriptor)

        # Check for policy, script type, or network mismatch
        policy_mismatch = self.key.policy_type != required_policy_type
        script_type_mismatch = (
            required_script_type is not None
            and self.key.script_type != required_script_type
        )
        network_mismatch = required_network and self.key.network != required_network

        if policy_mismatch or script_type_mismatch or network_mismatch:
            raise PolicyMismatchWarning(
                required_policy_type,
                required_script_type,
                self.key.policy_type,
                required_network,
                self.key.network,
            )

        # Validate that xpub matches descriptor requirements
        self._validate_xpub_match(descriptor, descriptor_xpubs)

    def load(self, wallet_data, qr_format):
        """Loads the wallet from the given data"""
        descriptor, label = parse_wallet(wallet_data)

        # convert descriptor keys to 'xpub' on same network -- for comparison only
        descriptor_xpubs = []
        for key in descriptor.keys:
            network, _ = version_to_network_versiontype(key.key.version)
            descriptor_xpubs.append(
                key.key.to_base58(version=NETWORKS[network]["xpub"])
            )

        if self.key:
            try:
                self._validate_descriptor(descriptor, descriptor_xpubs)
            except ValueError as e:
                raise ValueError("Invalid Descriptor: %s" % e)

        self.wallet_data = wallet_data
        self.wallet_qr_format = qr_format
        self.descriptor = to_unambiguous_descriptor(descriptor)
        self.label = label
        if self.descriptor.key and not self.descriptor.taptree:
            if not self.label:
                self.label = t("Single-sig")
            self.policy = {"type": self.descriptor.scriptpubkey_type()}
        elif self.descriptor.is_basic_multisig:
            m = int(str(self.descriptor.miniscript.args[0]))
            n = len(self.descriptor.keys)
            cosigners = [key.key.to_base58() for key in self.descriptor.keys]
            if self.descriptor.is_sorted:
                cosigners = sorted(cosigners)
            if not self.label:
                self.label = t("%d of %d multisig") % (m, n)

            self.policy = {
                "type": self.get_scriptpubkey_type(),
                "m": m,
                "n": n,
                "cosigners": cosigners,
            }
        elif self.descriptor.miniscript is not None or self.descriptor.taptree:
            if self.descriptor.taptree:
                if not descriptor.keys[0].origin:
                    from embit.ec import NUMS_PUBKEY

                    # Check if BIP-0341 NUMS was used
                    # Compare expected provably unspendable key with first descriptor key
                    if descriptor.keys[0].key.get_public_key() != NUMS_PUBKEY:
                        self.wallet_data = None
                        raise ValueError("Internal key not provably unspendable")
                taproot_txt = "TR "
                miniscript_type = P2TR
            else:
                taproot_txt = ""
                miniscript_type = P2WSH
            if not self.label:
                self.label = taproot_txt + t("Miniscript")
            cosigners = [key.key.to_base58() for key in self.descriptor.keys]
            cosigners = sorted(cosigners)
            self.policy = {
                "type": self.descriptor.scriptpubkey_type(),
                "cosigners": cosigners,
                "miniscript": miniscript_type,
            }

    def wallet_qr(self):
        """Returns the original wallet data and qr format for display back as a QR code"""
        if self.wallet_qr_format == FORMAT_BBQR:
            from .bbqr import encode_bbqr

            wallet_data = (
                self.wallet_data.encode("utf-8")
                if isinstance(self.wallet_data, str)
                else self.wallet_data
            )
            return encode_bbqr(wallet_data, file_type="U"), FORMAT_BBQR
        return (self.wallet_data, self.wallet_qr_format)

    def obtain_addresses(self, i=0, limit=None, branch_index=0):
        """Returns an iterator deriving addresses (default branch_index is receive)
        for the wallet up to the provided limit"""

        if self.descriptor is None:
            raise ValueError("No descriptor to derive addresses from")

        starting_index = i

        while limit is None or i < starting_index + limit:
            yield self.descriptor.derive(i, branch_index=branch_index).address(
                network=NETWORKS[self.which_network()]
            )
            i += 1

    def has_change_addr(self):
        """Returns if this wallet knows how to derive its change addresses"""

        return self.descriptor.num_branches > 1


def to_unambiguous_descriptor(descriptor):
    """If child derivation info is missing to generate receive addresses,
    use the default scheme
    """
    from embit.descriptor.arguments import KeyHash, AllowedDerivation

    if descriptor.key:
        if descriptor.key.allowed_derivation is None:
            descriptor.key.allowed_derivation = AllowedDerivation.default()
    else:
        for i in range(len(descriptor.miniscript.args)):
            key = descriptor.miniscript.args[i]
            if isinstance(key, (Key, KeyHash)):
                if key.allowed_derivation is None:
                    key.allowed_derivation = AllowedDerivation.default()
    return descriptor


def parse_key_value_file(wallet_data):
    """Tries to parse data as a key-value file"""
    key_vals = []
    for word in wallet_data.split(":"):
        for key_val in word.split("\n"):
            key_val = key_val.strip()
            if key_val != "":
                key_vals.append(key_val)

    keys_present = [key in key_vals for key in ["Format", "Policy", "Derivation"]]
    if any(keys_present):
        if not all(keys_present):
            raise KeyError(
                '"Format", "Policy", and "Derivation" keys not found in INI file'
            )

        script = key_vals[key_vals.index("Format") + 1].lower()
        if script not in (P2SH, P2SH_P2WSH, P2WSH):
            raise ValueError("invalid script type: %s" % script)

        policy = key_vals[key_vals.index("Policy") + 1]
        m = int(policy[: policy.index("of")].strip())
        n = int(policy[policy.index("of") + 2 :].strip())

        keys = []
        for i in range(len(key_vals)):
            kv = key_vals[i]
            kv_prefix = kv[:4].lower()
            if kv_prefix[1:] == "pub" and kv_prefix[0] in ["x", "z", "t", "v"]:
                xpub = Key.from_string(kv).key.to_base58()
                fingerprint = key_vals[i - 1]
                keys.append((xpub, fingerprint))

        if len(keys) != n:
            raise ValueError("expected %d keys, found %d" % (n, len(keys)))

        derivation = key_vals[key_vals.index("Derivation") + 1]

        keys.sort()
        keys = ["[%s/%s]%s" % (key[1], derivation[2:], key[0]) for key in keys]
        descriptor = None
        if script == P2SH:
            descriptor = Descriptor.from_string(
                ("sh(sortedmulti(%d," % m) + ",".join(keys) + "))"
            )

        if script == P2SH_P2WSH:
            descriptor = Descriptor.from_string(
                ("sh(wsh(sortedmulti(%d," % m) + ",".join(keys) + ")))"
            )

        if script == P2WSH:
            descriptor = Descriptor.from_string(
                ("wsh(sortedmulti(%d," % m) + ",".join(keys) + "))"
            )

        label = (
            key_vals[key_vals.index("Name") + 1]
            if key_vals.index("Name") >= 0
            else None
        )
        return descriptor, label
    return None, None


def parse_wallet(wallet_data):
    """Exhaustively tries to parse the wallet data from a known format, returning
    a descriptor and label if possible.

    If the descriptor cannot be derived, an exception is raised.
    """
    # pylint: disable=R0912

    # Check if wallet_data is a UR object without loading the UR module
    if wallet_data.__class__.__name__ == "UR":
        import urtypes

        # Try to parse as a Crypto-Output type
        try:
            output = urtypes.crypto.Output.from_cbor(wallet_data.cbor)
            return Descriptor.from_string(output.descriptor()), None
        except:
            pass

        # Try to parse as a Crypto-Account type
        try:
            account = urtypes.crypto.Account.from_cbor(
                wallet_data.cbor
            ).output_descriptors[0]
            return Descriptor.from_string(account.descriptor()), None
        except:
            pass

        # Treat the UR as a generic UR bytes object and extract the data for further processing
        wallet_data = urtypes.Bytes.from_cbor(wallet_data.cbor).data

    # Process as a string
    wallet_data = (
        wallet_data.decode() if not isinstance(wallet_data, str) else wallet_data
    )

    # Try to parse as JSON and look for a 'descriptor' key
    try:
        import ujson as json

        wallet_json = json.loads(wallet_data)
        if "descriptor" in wallet_json:
            descriptor = Descriptor.from_string(wallet_json["descriptor"])
            label = wallet_json["label"] if "label" in wallet_json else None
            return descriptor, label
        raise KeyError('"descriptor" key not found in JSON')
    except KeyError:
        raise ValueError("invalid wallet format")
    except:
        pass

    # Try to parse as a key-value file
    try:
        descriptor, label = parse_key_value_file(wallet_data)
        if descriptor and label:
            return descriptor, label
    except:
        raise ValueError("invalid wallet format")

    # Try to parse directly as a descriptor
    try:
        descriptor = Descriptor.from_string(wallet_data.strip())
        return descriptor, None
    except:
        pass

    raise ValueError("invalid wallet format")


def parse_address(address_data):
    """Exhaustively tries to parse an address from a known format, returning
    the address if possible.

    If the address cannot be derived, an exception is raised.
    """
    from embit.script import Script, address_to_scriptpubkey

    addr = address_data
    sc = None
    if address_data.lower().startswith("bitcoin:"):
        addr_end = address_data.find("?")
        if addr_end == -1:
            addr_end = len(address_data)
        addr = address_data[8:addr_end]

    if addr == addr.upper():
        # bip173 suggests bech32 in uppercase for compact QR-Code
        try:
            sc = address_to_scriptpubkey(addr.lower())
            if isinstance(sc, Script):
                return addr.lower()
        except:
            pass

    if not isinstance(sc, Script):
        try:
            address_to_scriptpubkey(addr)
        except:
            raise ValueError("invalid address")

    return addr


def version_to_network_versiontype(hdkey_version):
    """returns embit.networks.NETWORKS[network][versiontype] keys
    based on HDKey's version bytes"""
    network, versiontype = None, None
    for netname, versiontypes in NETWORKS.items():
        if hdkey_version in versiontypes.values():
            network = netname
            versiontype = [k for k, v in versiontypes.items() if v == hdkey_version][0]
            break
    return network, versiontype


def is_double_mnemonic(mnemonic: str):
    """Check if the mnemonic is a double mnemonic (12+12+24)"""

    words = mnemonic.split(" ")
    if len(words) > 12:
        from .bip39 import k_mnemonic_is_valid

        if (
            k_mnemonic_is_valid(" ".join(words[:12]))
            and k_mnemonic_is_valid(" ".join(words[12:]))
            and k_mnemonic_is_valid(mnemonic)
        ):
            return True

    return False
