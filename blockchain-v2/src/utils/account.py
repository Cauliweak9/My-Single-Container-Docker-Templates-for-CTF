from eth_account.hdaccount import key_from_seed, seed_from_mnemonic
from eth_account import Account


DEFAULT_DERIVATION_PATH = "m/44'/60'/0'/0/"


def get_account(mnemonic: str, index: int):
    seed = seed_from_mnemonic(mnemonic, "")
    private_key = key_from_seed(seed, f"{DEFAULT_DERIVATION_PATH}{index}")
    return Account.from_key(private_key)


def get_player_account(mnemonic: str):
    return get_account(mnemonic, 0)


def get_system_account(mnemonic: str):
    return get_account(mnemonic, 1)


def get_additional_account(mnemonic: str, index: int):
    return get_account(mnemonic, index + 2)
