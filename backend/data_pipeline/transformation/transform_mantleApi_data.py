from typing import List
from ..schemas.data_schemas import TokenBalance


def transform_balance(balance_data:float)->float|None:
    if not balance_data:
        return None
    
    return TokenBalance(
        balance=balance_data
    )