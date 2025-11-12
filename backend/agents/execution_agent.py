from core.config import REDIS_CONNECT
from core.pubsub.channel_manager import ChannelNames

class execution_agent:
    def __init__(self):
        self.redis_db = REDIS_CONNECT

    # Receives automation complete data from automation_agent
    async def Receive_execution_data(self):
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.EXECUTION.value)

        async for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            data = message['data']
            print(f"Received execution data: {data}")
            # Process the execution data as needed

            """"
                Execution logic can be implemented here
            """

            # publish the final execution data to other systems or agents as needed.
            await self.redis_db.publish('execution_complete_channel', data)
