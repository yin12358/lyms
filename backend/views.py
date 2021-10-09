import asyncio
import base64
import datetime
import time

import websockets

from django.shortcuts import render

# Create your views here.


from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

import json

# 解决前端post请求 csrf问题

from django.views.decorators.csrf import csrf_exempt


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

@csrf_exempt
def testapi(request):
    n = asyncio.new_event_loop()
    asyncio.set_event_loop(n)
    n.run_until_complete(websockets.serve(echo, '47.98.113.173', 9026))
    # n.run_until_complete(websockets.serve(echo, '47.98.113.173', 9001))
    n.run_forever()
    print("结束")
    resp = {'errorcode': 100, 'type': 'Get', 'data': {'main': request.GET.get('aa')}}
    return HttpResponse(json.dumps(resp), content_type="application/json")
