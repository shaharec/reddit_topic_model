"""Test suite for the BankAccount demo codebase.

Against the shipped (buggy) implementation: 2 tests pass, 3 tests fail.
The harness must make all 5 pass by fixing account.py only.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from account import BankAccount


def test_deposit_increases_balance():
    acc = BankAccount("alice", 100.0)
    acc.deposit(50.0)
    assert acc.balance == 150.0


def test_withdraw_reduces_balance():
    acc = BankAccount("alice", 100.0)
    acc.withdraw(40.0)
    assert acc.balance == 60.0


def test_withdraw_overdraft_raises():
    acc = BankAccount("alice", 100.0)
    with pytest.raises(ValueError):
        acc.withdraw(150.0)  # fails: Bug 1 lets the balance go negative
    assert acc.balance == 100.0


def test_transfer_moves_full_amount():
    src = BankAccount("alice", 100.0)
    dst = BankAccount("bob", 0.0)
    src.transfer(dst, 60.0)
    assert src.balance == 40.0
    assert dst.balance == 60.0  # fails: Bug 2 only credits half


def test_transfer_insufficient_funds_raises():
    src = BankAccount("alice", 10.0)
    dst = BankAccount("bob", 0.0)
    with pytest.raises(ValueError):
        src.transfer(dst, 50.0)  # fails: Bug 1 lets the withdrawal through
    assert src.balance == 10.0
    assert dst.balance == 0.0
