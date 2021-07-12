from .base import WordlistBase as _WordlistBase
import uembit as _uembit

WORDLIST = _WordlistBase(_uembit.wordlists.bip39)
