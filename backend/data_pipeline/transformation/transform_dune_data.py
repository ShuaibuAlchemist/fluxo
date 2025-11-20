from typing import List
from ..schemas.data_schemas import UserPortfolio

def transform_user_portfolio(user_portfolio_data:List,wallet_address)->List[UserPortfolio]|None:
    if not user_portfolio_data:
        return None
        
    transformed_portfolio_data = []
    for token_balance in user_portfolio_data:
        
        transformed_portfolio_data.append(UserPortfolio(
            user_address=wallet_address,
            token_address=token_balance['token_address'],
            token_symbol=token_balance['token_symbol'],
            balance=token_balance['balance'],
            value_usd=token_balance['value_usd'],
            price_usd=token_balance['price_usd'],
            percentage_of_portfolio=token_balance['percentage_of_portfolio']
        ))
    
    return transformed_portfolio_data

