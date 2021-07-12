from ..base import EmbitError


class DescriptorError(EmbitError):
    pass


class MiniscriptError(DescriptorError):
    pass


class ArgumentError(MiniscriptError):
    pass


class KeyError(ArgumentError):
    pass
