from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames

class macro_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        
    # Receives macroeconomic data from relevant sources
    async def Receive_macro_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.MACRO.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received macro data: {data}")
            # Process the macro data as needed

            """"
                Macroeconomic analysis logic can be implemented here
            """

            # publish the processed macro data to other agents listening.
            await self.redis_db.publish('macro_processed_channel', data)
