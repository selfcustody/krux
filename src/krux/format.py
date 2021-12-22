SATS_PER_BTC = 100000000

def satcomma(amount):
    """Formats a BTC amount according to the Satcomma standard:
       https://medium.com/coinmonks/the-satcomma-standard-89f1e7c2aede
    """
    amount_str = '%.8f' % round(amount / SATS_PER_BTC, 8)
    msb = amount_str[:-9] # most significant bitcoin heh heh heh
    lsb = amount_str[len(msb)+1:]
    return _add_commas(msb, ( ',' )) + ( '.' ) + _add_commas(lsb, ( ',' ))

def _add_commas(number, comma_sep=','):
    """Returns a number separated with commas"""
    triplets_num = len(number) // 3
    remainder = len(number) % 3
    triplets = [number[:remainder]] if remainder else []
    triplets += [number[remainder+i*3:remainder+3+i*3] for i in range(triplets_num)]
    return comma_sep.join(triplets)
