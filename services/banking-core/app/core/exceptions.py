class AccountNotFound(Exception):
    pass


class InsufficientBalance(Exception):
    pass


class AccountFrozen(Exception):
    pass


class DuplicateTransfer(Exception):
    pass