import asyncio
import aiohttp
from typing import Dict, Any


class ExternalService:
    def __init__(self):
        pass


    async def dex_screener_price_data(self,token_address:str)->Dict[str,Any]|None:
        if not isinstance(token_address,str):
            return 
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    if not result:
                        return
                    
                    pair_data = result.get('pairs',[])
                    if not pair_data:
                        return
                    
                    pairs_data_info = pair_data[0]
                    price = pairs_data_info.get('priceUsd',0)
                    price_change_1hr = pairs_data_info.get('priceChange').get('h1')

                    price_info:Dict[str,Any] = {
                        'price':price,
                        'price_change_1hr':price_change_1hr
                    }
                    return price_info

