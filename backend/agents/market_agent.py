from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames

class market_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT

    # Receives whale market data from onchain_agent
    async def Receive_market_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.MARKET_DATA.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received market data: {data}")
            # Process the market data as needed

            """"
                Market data processing logic can be implemented here
            """

            # publish the processed market data to other agents listening.
            await self.redis_db.publish('processed_market_data_channel', data)