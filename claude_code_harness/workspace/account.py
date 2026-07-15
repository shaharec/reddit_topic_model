"""A small BankAccount 'codebase' used to evaluate the harness.

It intentionally ships with two real bugs (see tests/test_account.py:
3 of the 5 tests fail against this implementation). The harness's job
is to fix the implementation only -- never the tests.

Bug 1: withdraw() allows overdrafts instead of raising ValueError.
Bug 2: transfer() only credits half of the amount to the destination account.
"""


class BankAccount:
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        # BUG 1: no overdraft check -- should raise ValueError when
        # amount > self.balance instead of letting the balance go negative.
        self.balance -= amount
        return self.balance

    def transfer(self, other: "BankAccount", amount: float) -> None:
        self.withdraw(amount)
        # BUG 2: only half of the withdrawn amount reaches the other account.
        other.deposit(amount * 0.5)
