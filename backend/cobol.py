import ctypes
from dataclasses import dataclass
import json
from mpmath import mp
from typing import List

create_account_lib = ctypes.CDLL('./create-account.so')
read_account_lib = ctypes.CDLL('./read-account.so')
read_accounts_lib = ctypes.CDLL('./read-accounts.so')
create_transaction_lib = ctypes.CDLL('./create-transaction.so')
read_credits_lib = ctypes.CDLL('./read-credits.so')
read_debits_lib = ctypes.CDLL('./read-debits.so')
process_transactions_lib = ctypes.CDLL('./process-transactions.so')

mp.dps = 113

Comp3Type = ctypes.c_ubyte * 16
Char4Type = ctypes.c_char * 4


class Account(ctypes.Structure):
    _fields_ = [
        ("accountikey", (ctypes.c_char * 4)),
        ("accountbalancetotal", Comp3Type),
        ("lastcredittransaction", (ctypes.c_char * 4)),
        ("lastdebittransaction", (ctypes.c_char * 4))
    ]


class Accounts(ctypes.Structure):
    _fields_ = [("accounts", Account * 10)]


@dataclass
class UserAccount:
    account_id: str
    amount: str
    last_credit_transaction: str
    last_debit_transaction: str


@dataclass
class UserAccounts:
    accounts: List[UserAccount]


class Transaction(ctypes.Structure):
    _fields_ = [
        ("transactionikey", (ctypes.c_char * 4)),
        ("sourceid", (ctypes.c_char * 4)),
        ("destinationid", (ctypes.c_char * 4)),
        ("transactionamount", Comp3Type),
        ("dateyyyy", (ctypes.c_char * 4)),
        ("datemm", (ctypes.c_char * 2)),
        ("datedd", (ctypes.c_char * 2)),
        ("timehh", (ctypes.c_char * 2)),
        ("timemm", (ctypes.c_char * 2)),
        ("timess", (ctypes.c_char * 2)),
        ("timems", (ctypes.c_char * 6))
    ]


class Transactions(ctypes.Structure):
    _fields_ = [("transactions", Transaction * 10)]


@dataclass
class AccountTransaction:
    transaction_id: str
    source_id: str
    destination_id: str
    amount: str
    date_yyyy: str
    date_mm: str
    date_dd: str
    time_hh: str
    time_mm: str
    time_ss: str
    time_ms: str


@dataclass
class AccountTransactions:
    transactions: List[AccountTransaction]


def create_account(id, balance_total):
    useraccountikey = (Char4Type)(*f"{id:04d}".encode('ascii'))
    useraccountbalancetotal = str_to_comp3_s9_29_v99(balance_total)
    account = Account()
    returncode = ctypes.create_string_buffer(2)
    create_account_lib.createaccount(ctypes.byref(useraccountikey), ctypes.byref(
        useraccountbalancetotal), ctypes.byref(account), ctypes.byref(returncode))
    return_code = returncode.value.decode("utf-8")
    if return_code != "00":
        return None, return_code
    account_id = account.accountikey.decode("utf-8")
    account_balance_total = comp3_s9_29_v99_to_mpmath(
        account.accountbalancetotal)
    last_credit_transaction = account.lastcredittransaction.decode("utf-8")
    last_debit_transaction = account.lastdebittransaction.decode("utf-8")
    user_account = UserAccount(account_id=account_id, amount=str(
        account_balance_total), last_credit_transaction=last_credit_transaction, last_debit_transaction=last_debit_transaction)
    return user_account, return_code


def read_account(id):
    useraccountikey = (Char4Type)(*f"{id:04d}".encode('ascii'))
    account = Account()
    returncode = ctypes.create_string_buffer(2)
    read_account_lib.readaccount(ctypes.byref(
        useraccountikey), ctypes.byref(account), ctypes.byref(returncode))
    return_code = returncode.value.decode("utf-8")
    if return_code != "00":
        return None, return_code
    account_id = account.accountikey.decode("utf-8")
    account_balance_total = comp3_s9_29_v99_to_mpmath(
        account.accountbalancetotal)
    last_credit_transaction = account.lastcredittransaction.decode("utf-8")
    last_debit_transaction = account.lastdebittransaction.decode("utf-8")
    user_account = UserAccount(account_id=account_id, amount=str(
        account_balance_total), last_credit_transaction=last_credit_transaction, last_debit_transaction=last_debit_transaction)
    return user_account, return_code


def read_accounts():
    accounts = Accounts()
    returncode = ctypes.create_string_buffer(2)
    read_accounts_lib.readaccounts(
        ctypes.byref(accounts), ctypes.byref(returncode))
    return_code = returncode.value.decode("utf-8")
    if return_code != "00":
        return None, return_code
    user_accounts = [
        UserAccount(
            account_id=record.accountikey.decode("utf-8"),
            amount=str(comp3_s9_29_v99_to_mpmath(record.accountbalancetotal)),
            last_credit_transaction=record.lastcredittransaction.decode(
                "utf-8"),
            last_debit_transaction=record.lastdebittransaction.decode("utf-8")
        )
        for record in accounts.accounts if record.accountikey.decode("utf-8") != ''
    ]
    return UserAccounts(accounts=user_accounts), return_code


def create_transaction(account_id, destination_id, transaction_amount):
    _, return_code = read_account(account_id)
    if return_code != "00":
        return None, return_code
    _, return_code = read_account(destination_id)
    if return_code != "00":
        return None, return_code

    accountikey = (Char4Type)(*f"{account_id:04d}".encode('ascii'))
    destinationikey = (Char4Type)(*f"{destination_id:04d}".encode('ascii'))
    amountvalue = str_to_comp3_s9_29_v99(transaction_amount)
    transaction = Transaction()
    returncode = ctypes.create_string_buffer(2)
    create_transaction_lib.createtransaction(ctypes.byref(accountikey), ctypes.byref(destinationikey),
                                             ctypes.byref(amountvalue), ctypes.byref(transaction), ctypes.byref(returncode))
    return_code = returncode.value.decode("utf-8")
    if return_code != "00":
        return None, return_code
    transaction_value = AccountTransaction(
        transaction_id=transaction.transactionikey.decode("utf-8"),
        source_id=transaction.sourceid.decode("utf-8"),
        destination_id=transaction.destinationid.decode("utf-8"),
        amount=str(comp3_s9_29_v99_to_mpmath(transaction.transactionamount)),
        date_yyyy=transaction.dateyyyy.decode("utf-8"),
        date_mm=transaction.datemm.decode("utf-8"),
        date_dd=transaction.datedd.decode("utf-8"),
        time_hh=transaction.timehh.decode("utf-8"),
        time_mm=transaction.timemm.decode("utf-8"),
        time_ss=transaction.timess.decode("utf-8"),
        time_ms=transaction.timems.decode("utf-8")
    )
    return transaction_value, return_code


def read_credit_transactions(account_id, start_transaction_id):
    accountikey = (Char4Type)(*f"{account_id:04d}".encode('ascii'))
    starttransactionikey = (Char4Type)(
        *f"{start_transaction_id:04d}".encode('ascii'))
    accounttransactions = Transactions()
    returncode = ctypes.create_string_buffer(2)
    read_credits_lib.readcredits(ctypes.byref(accountikey), ctypes.byref(
        starttransactionikey), ctypes.byref(accounttransactions), ctypes.byref(returncode))
    return_code = returncode.value.decode("utf-8")
    if return_code != "00" and return_code != "03":
        return None, return_code
    credit_transactions = [
        AccountTransaction(
            transaction_id=record.transactionikey.decode("utf-8"),
            source_id=record.sourceid.decode("utf-8"),
            destination_id=record.destinationid.decode("utf-8"),
            amount=str(comp3_s9_29_v99_to_mpmath(record.transactionamount)),
            date_yyyy=record.dateyyyy.decode("utf-8"),
            date_mm=record.datemm.decode("utf-8"),
            date_dd=record.datedd.decode("utf-8"),
            time_hh=record.timehh.decode("utf-8"),
            time_mm=record.timemm.decode("utf-8"),
            time_ss=record.timess.decode("utf-8"),
            time_ms=record.timems.decode("utf-8")
        )
        for record in accounttransactions.transactions if record.transactionikey.decode("utf-8") != ''
    ]
    return AccountTransactions(transactions=credit_transactions), return_code


def read_debit_transactions(account_id, start_transaction_id):
    accountikey = (Char4Type)(*f"{account_id:04d}".encode('ascii'))
    starttransactionikey = (Char4Type)(
        *f"{start_transaction_id:04d}".encode('ascii'))
    accounttransactions = Transactions()
    returncode = ctypes.create_string_buffer(2)
    read_debits_lib.readdebits(ctypes.byref(accountikey), ctypes.byref(
        starttransactionikey), ctypes.byref(accounttransactions), ctypes.byref(returncode))
    return_code = returncode.value.decode("utf-8")
    if return_code != "00" and return_code != "03":
        return None, return_code
    debit_transactions = [
        AccountTransaction(
            transaction_id=record.transactionikey.decode("utf-8"),
            source_id=record.sourceid.decode("utf-8"),
            destination_id=record.destinationid.decode("utf-8"),
            amount=str(comp3_s9_29_v99_to_mpmath(record.transactionamount)),
            date_yyyy=record.dateyyyy.decode("utf-8"),
            date_mm=record.datemm.decode("utf-8"),
            date_dd=record.datedd.decode("utf-8"),
            time_hh=record.timehh.decode("utf-8"),
            time_mm=record.timemm.decode("utf-8"),
            time_ss=record.timess.decode("utf-8"),
            time_ms=record.timems.decode("utf-8")
        )
        for record in accounttransactions.transactions if record.transactionikey.decode("utf-8") != ''
    ]
    return AccountTransactions(transactions=debit_transactions), return_code


def process_transactions(account_id):
    accountikey = (Char4Type)(*f"{account_id:04d}".encode('ascii'))
    returncode = ctypes.create_string_buffer(2)
    process_transactions_lib.processtransactions(
        ctypes.byref(accountikey), ctypes.byref(returncode))
    return_code = returncode.value.decode("utf-8")
    return return_code


def str_to_comp3_s9_29_v99(value_str):
    value_str = value_str.strip()
    if not value_str.replace('.', '').replace('-', '').isdigit():
        raise ValueError("Invalid numeric string for conversion.")

    # Determine the sign
    is_negative = value_str.startswith('-')
    value_str = value_str.lstrip('-')

    # Separate integer and decimal parts
    if '.' in value_str:
        integer_part, decimal_part = value_str.split('.')
        decimal_part = decimal_part[:2].ljust(
            2, '0')  # Limit to 2 decimal places
    else:
        integer_part = value_str
        decimal_part = '00'

    # Pad integer part to 29 digits
    if len(integer_part) > 29:
        raise ValueError("Integer part exceeds 29 digits for PIC 9(29)V99.")
    integer_part = integer_part.zfill(29)

    # Combine integer and decimal parts
    packed_value = integer_part + decimal_part

    # Convert to packed decimal (COMP-3)
    packed_bytes = bytearray()
    for i in range(0, len(packed_value) - 1, 2):
        packed_bytes.append(int(f"0x{packed_value[i:i+2]}", 16))

    # Set the last byte with the sign nibble
    last_digit = packed_value[-1]
    sign_nibble = 0x0C if not is_negative else 0x0D
    last_byte = ((int(f"0x{last_digit}", 16)) << 4) | sign_nibble
    packed_bytes.append(last_byte)

    # Adjust to 16 bytes (31 digits -> 16 bytes)
    if len(packed_bytes) < 16:
        packed_bytes = (b'\x00' * (16 - len(packed_bytes))) + packed_bytes
    elif len(packed_bytes) > 16:
        raise ValueError(
            "Packed value exceeds the 16-byte size for S9(29)V99.")

    # Convert to ctypes.c_ubyte array
    c_ubyte_array = (Comp3Type)(*packed_bytes)
    return c_ubyte_array


def comp3_s9_29_v99_to_mpmath(data_bytes: bytes, decimal_places: int = 2):
    if all(b == 0 for b in data_bytes):
        return mp.mpf(0.0)

    nibbles = []
    for byte in data_bytes:
        nibbles.append(byte >> 4)
        nibbles.append(byte & 0x0F)

    sign_nibble = nibbles.pop()

    if sign_nibble == 0xD:
        sign = -1
    elif sign_nibble in (0xC, 0xF):
        sign = 1
    else:
        raise ValueError("Invalid sign nibble in COMP-3")

    digits = ''.join(str(d) for d in nibbles)
    if len(digits) < decimal_places:
        digits = digits.zfill(decimal_places + 1)

    int_part = digits[:-decimal_places] or '0'
    dec_part = digits[-decimal_places:]
    return sign * mp.mpf(f"{int_part}.{dec_part}")
