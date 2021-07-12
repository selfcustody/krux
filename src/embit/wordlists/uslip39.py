from .base import WordlistBase as _WordlistBase
import uembit as _uembit

SLIP39_WORDS = _WordlistBase(_uembit.wordlists.slip39)
