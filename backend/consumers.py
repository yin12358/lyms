import asyncio
import base64
import datetime
import json
import time

import nest_asyncio
import websockets

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

# My Stuff
# from support_apps.base_app.support import md5_hashlib
from django.http import HttpResponse

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
        print("开启连接")
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
        print("关闭连接")
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
        print("广播发送")
        print(event)
        await self.send(text_data=json.dumps({
            'message': event.get('text')
        }))



def num1(req_id):
    with open("C:/Users/lenovo/Desktop/a/a.jpg", 'rb') as f:
        tp = f.read()
    t = datetime.datetime.now()

    # 当前日期
    t1 = t.strftime('%Y-%m-%d 00:00:00')
    # 转为秒级时间戳
    start_time = time.mktime(time.strptime(t1, '%Y-%m-%d %H:%M:%S'))
    # 转为毫秒级
    # 30天后
    t2 = (t + datetime.timedelta(days=30)).strftime("%Y-%m-%d 00:00:00")
    # 转为秒级时间戳
    end_time = time.mktime(time.strptime(t2, '%Y-%m-%d %H:%M:%S'))
    tp2 = base64.b64encode(tp)
    tp3 = str(tp2, encoding="utf-8")
    datas = {
        "LibID": 2,
        "PersonInfo": {
            "Name": "凌风",
            "Code": "6",
            "Remark": "",
            "ICCode": "",
            "IDCode": "",
            "TempID": "",
            "PermTime": "0,0",
            "Img1": {
                "ImgId": 1,
                "Size": len(tp3),
                "Data": tp3
            }
        }
    }
    tjry_datass = {
        "method": "Post",
        "uri": "/api/v1.0/rdc/data/person",
        "req_id": req_id,  # 用于区分哪个服务器发送的数据
        "data": datas
    }
    d = json.dumps(tjry_datass)
    return d


async def echo(websocket, path):
    print("开始添加人脸信息")
    result = await websocket.recv()
    response = json.loads(result)
    zc = {"req_id": response['req_id'], "data": {}, "code": 0, "msg": ""}
    await websocket.send(json.dumps(zc))
    print("开始发送")
    await websocket.send(num1(response['req_id']))
    new_result = await websocket.recv()
    tjry_result = json.loads(new_result)
    if tjry_result['code'] == 0:
        print('添加成功')
    elif tjry_result['code'] == 1004:
        print("重复添加")
    asyncio.get_event_loop().stop()

class NewMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # print("自动执行开启连接")
        # n = asyncio.new_event_loop()
        # asyncio.set_event_loop(n)
        # print(222222)
        # # await n.run_until_complete(websockets.serve(echo, '121.40.214.42', 9599))
        # asyncio.ensure_future(websockets.serve(echo, '121.40.214.42', 9599), loop=n)
        #
        # print(999999)
        # # n.run_until_complete(websockets.serve(echo, '47.98.113.173', 9001))
        # await n.run_forever()
        # print("结束")
        print("自动执行开启连接")
        # n = asyncio.new_event_loop()
        # asyncio.set_event_loop(n)
        print(222222)
        asyncio.get_event_loop().run_until_complete(websockets.serve(echo, '121.40.214.42', 9005))
        # asyncio.ensure_future(websockets.serve(echo, '121.40.214.42', 9599), loop=n)

        print(999999)
        # n.run_until_complete(websockets.serve(echo, '47.98.113.173', 9001))
        asyncio.get_event_loop().run_forever()
        print("结束")


    def testapi(self,request):
        print(11111111111)
        nest_asyncio.apply()
        n = asyncio.new_event_loop()
        asyncio.set_event_loop(n)
        n.run_until_complete(websockets.serve(echo, '121.40.214.42', 9599))
        # n.run_until_complete(websockets.serve(echo, '47.98.113.173', 9001))
        n.run_forever()
        print("结束")
        resp = {'errorcode': 100, 'type': 'Get', 'data': {'main': request.GET.get('aa')}}
        return HttpResponse(json.dumps(resp), content_type="application/json")