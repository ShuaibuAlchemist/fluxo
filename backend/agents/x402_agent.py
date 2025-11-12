from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames

class x402_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        
    # Receives x402 specific data from relevant tasks
    async def Receive_x402_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.X402.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received x402 data: {data}")
            # Process the x402 data as needed

            """"
                x402 specific logic can be implemented here
            """

            # publish the processed x402 data to other agents listening.
            await self.redis_db.publish('x402_processed_channel', data)