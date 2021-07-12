from . import ec
from .script import Witness, Script
from .transaction import Transaction

def parse_multisig(sc):
    d = sc.data
    if d[-1] != 0xae:
        raise RuntimeError("Not multisig")
    m = d[0]-80
    n = d[-2]-80
    if m > n or m < 1 or n < 1 or m > 16 or n > 16:
        raise RuntimeError("Invalid m or n in multisig script")
    pubs = d[1:-2]
    if len(pubs) % 34 != 0:
        raise RuntimeError("Pubkeys of strange length")
    if len(pubs) != 34*n:
        raise RuntimeError("Not enough pubkeys")
    pubkeys = [ec.PublicKey.parse(pubs[i*34+1:(i+1)*34]) for i in range(n)]
    return m, pubkeys

def finalize_psbt(tx, ignore_missing=False):
    # ugly copy
    ttx = Transaction.parse(tx.tx.serialize())
    done = 0
    for i, inp in enumerate(ttx.vin):
        if tx.utxo(i).script_pubkey.script_type() == "p2pkh":
            d = b""
            # meh, ugly, doesn't check pubkeys
            for k in tx.inputs[i].partial_sigs:
                v = tx.inputs[i].partial_sigs[k]
                d += bytes([len(v)]) + v + bytes([len(k.sec())]) + k.sec()
            ttx.vin[i].script_sig = Script(d)
            done += 1
            continue

        if tx.inputs[i].redeem_script is not None:
            ttx.vin[i].script_sig = Script(tx.inputs[i].redeem_script.serialize())

        # if multisig
        if tx.inputs[i].witness_script is not None:
            m, pubs = parse_multisig(tx.inputs[i].witness_script)
            sigs = []
            for pub in pubs:
                if pub in tx.inputs[i].partial_sigs:
                    sigs.append(tx.inputs[i].partial_sigs[pub])
                if len(sigs) == m:
                    break
            if len(sigs) == m or ignore_missing:
                inp.witness = Witness([b""] + sigs + [tx.inputs[i].witness_script.data])
                done += 1
            continue

        # meh, ugly, doesn't check pubkeys
        for k in tx.inputs[i].partial_sigs:
            v = tx.inputs[i].partial_sigs[k]
            arr = [v, k.sec()]
            # if tx.inputs[i].redeem_script:
            #     arr = [tx.inputs[i].redeem_script.data] + arr
            inp.witness = Witness(arr)
            done += 1

        # TODO: legacy
    if not ignore_missing and done < len(ttx.vin):
        return None
    return ttx

