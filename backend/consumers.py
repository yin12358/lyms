import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

# My Stuff
# from support_apps.base_app.support import md5_hashlib
from backend.support import md5_hashlib


def send_group_msg(group_name, data):
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name, {
            "type": "chat.message",
            "text": data,
        })


def send_channel_msg(channel_name, data):
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(
        channel_name, {
            "type": "chat.message",
            "text": data,
        })


class MessageConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # 开启一个新的连接，连接包含消息通道层，通道层的名称
        models_name = self.scope['url_route']['kwargs']['models_name']
        hotel_group_id = self.scope['user_info']['hotel_group_id']
        hotel_id = self.scope['user_info']['hotel_id']
        self.group_name = md5_hashlib("{}{}{}".format(hotel_group_id, hotel_id, models_name))
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 关闭连接
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # # 从客户端接收消息，将消息推送到消息组
    # async def receive(self, text_data):
    # 发送消息到频道组
    # await self.channel_layer.group_send(
    #     self.room_group_name,
    #     {
    #         'type': 'chat.message',
    #         'text': text_data,
    #         'username': 'test_user'
    #     }
    # )
    # 单独发消息到指定的频道
    # await self.channel_layer.send(
    #     self.channel_name,
    #     {
    #         'type': 'chat.message',
    #         'text': text_data,
    #     })

    # 从消息组接收消息，进行广播
    async def chat_message(self, event):
        print(event)
        await self.send(text_data=json.dumps({
            'message': event.get('text')
        }))
