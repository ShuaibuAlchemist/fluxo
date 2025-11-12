from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames

class portfolio_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        

    # Receives processed market data from market_agent
    async def Receive_portfolio_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.PORTFOLIO.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received portfolio data: {data}")
            # Process the portfolio data as needed

            """"
                Portfolio management logic can be implemented here
            """

            # publish the final portfolio data to other agents listening.
            await self.redis_db.publish('final_portfolio_channel', data)