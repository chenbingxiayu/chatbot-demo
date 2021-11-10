import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger('django')


class AssignmentConsumer(AsyncJsonWebsocketConsumer):
    """
    Websocket Consumer that notify staff of new assignment of student
    """

    async def connect(self):
        """
        Establish connection from chat console of staff

        :return:
        """
        if hasattr(self.scope['user'], 'netid'):
            staff_id = self.scope['user'].netid
            if not staff_id:
                return
        else:
            return

        # This is a staff specific group
        self.groupname = f"staff_{staff_id}"
        await self.channel_layer.group_add(
            self.groupname,
            self.channel_name
        )

        # This is an universal group
        await self.channel_layer.group_add(
            'staff',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.groupname,
                self.channel_name
            )
        except Exception as e:
            logger.exception(e)
            logger.error("Error when disconnect websocket")
            logger.error(f"self.groupname: {self.groupname}")
            logger.error(f"self.channel_name: {self.channel_name}")

    async def receive_json(self, content, **kwargs):
        pass

    # async def send_assignment_alert(cls, event):
    #     logger.info('send assignment alert to frontend')
    #     if event.get('content'):
    #         await cls.send_json(event['content'])

    async def refresh_chat_queue(self, event):
        logger.info('waiting queue updated')
        if event.get('content'):
            await self.send_json(event['content'])
