class InvalidStateException(Exception):
    """The state is not valid."""

    pass


class InvalidRegexException(Exception):
    """The Regex is not valid."""

    pass

class DFAInvalidArgumentsException(Exception):
    """The DFA arguments are not valid."""

    pass
