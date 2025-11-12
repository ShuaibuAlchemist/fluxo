from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames

class automation_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT

    # Receives final portfolio data from portfolio_agent
    async def Receive_automation_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.AUTOMATION.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received automation data: {data}")
            # Process the automation data as needed

            """"
                Automation logic can be implemented here
            """

            # publish the final automation data to other systems or agents as needed.
            await self.redis_db.publish('automation_complete_channel', data)