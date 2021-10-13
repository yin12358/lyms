#! -*- coding: utf-8 -*-

import asyncio
import json
import websockets

# 创建websocket连接列表
websocket_users = set()

# 处理业务请求类
class func_process(object):

    # 注册、心跳、过人记录解析
    def cmd_dispose(self, data_json):
        uri = data_json["uri"]
        print("处理 ： " + str(uri))
        req_id = data_json["req_id"]
        print("处理 ： " + str(req_id))
        # 处理websocket业务，组装报文
        req_data = ""
        while True:
            if "regist" in uri:
                req_data = {
                    "req_id": req_id,
                    "code": 0,
                    "msg": "",
                    "data": {
                        "Heart": {},
                        "Rcd": {}
                    }
                }
                break
            elif "heart" in uri:
                req_data = {
                    "req_id": req_id,
                    "code": 0,
                    "msg": "",
                    "data": {
                        "Heart": {},
                        "Rcd": {}
                    }
                }
                break
            elif "rcd" in uri:
                # 过人记录图片数据
                pic_data = data_json["data"]["ImgSmall"]["Data"]
                break
            else:
                print("异常处理请求")

        return req_data

# 接收客户端消息并处理，这里只是简单把客户端发来的返回回去
async def recv_user_msg(websocket):
    # 数据解析函数
    take = func_process()
    while True:
        try:
            # 接受数据
            recv_text = await websocket.recv()
            print("recv_text:", websocket.pong, recv_text + "\n")
            # 解析数据
            data_json = json.loads(recv_text)
            print(data_json)
            if "uri" in data_json:
                # 处理注册、心跳、过人记录请求业务
                send_date = take.cmd_dispose(data_json)
                print("发送数据:", str(send_date) + "\n")
                # 回复注册、心跳请求业务
                await websocket.send(json.dumps(send_date))
            else:
                # 其他业务处理流程
                print("异常数据2")
        except:
            # 异常处理流程
            print("异常数据1")

# 服务器端主逻辑
async def run(websocket, path):
    while True:
        try:
            # 添加websocket连接至列表中
            websocket_users.add(websocket)
            print("websocket_users list:", websocket_users)
            # 回复消息
            await recv_user_msg(websocket)
        except websockets.ConnectionClosed:
            # 链接断开
            print("ConnectionClosed...", path)
            websocket_users.remove(websocket)
            break
        except websockets.InvalidState:
            # 无效状态
            print("InvalidState...")
            break
        except Exception as e:
            print("Exception:", e)

if __name__ == '__main__':
    print("192.168.0.128:8181 websocket...")
    # asyncio.get_event_loop().run_until_complete(websockets.serve(run, "192.168.0.128", 8181))
    asyncio.get_event_loop().run_until_complete(websockets.serve(run, "121.40.214.42", 9599))
    asyncio.get_event_loop().run_forever()
