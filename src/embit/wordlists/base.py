class WordlistBase:
    def __init__(self, mod):
        self._mod = mod

    def __getitem__(self, n):
        if isinstance(n, slice):
            (start, stop, step) = (n.start or 0, n.stop if n.stop is not None else len(self), n.step or 1)
            if start < 0:
                start += len(self)
            if stop < 0:
                stop += len(self)
            return [self._mod.get(i) for i in range(start, stop, step)]
        if n < 0:
            n = len(self) + n
        if n >= len(self):
            raise IndexError
        return self._mod.get(n)

    def __len__(self):
        return self._mod.len

    def index(self, word):
        idx = self._mod.index(word)
        if idx < 0:
            raise ValueError
        return idx

    def __contains__(self, word):
        return (self._mod.index(word) >= 0)