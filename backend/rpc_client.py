#  -*- coding: utf-8 -*-
import os
import sys
import json
import logging
import datetime

import zerorpc
from django.conf import settings
from django.http import HttpRequest
from flask.globals import LocalProxy
from django.shortcuts import HttpResponseRedirect
from rest_framework.request import Request
from rest_framework.response import Response

logger = logging.getLogger(__name__)
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)

"""token检查的RPC客户端"""
server = settings.AUTHORIZATION_RPC_CLIENT  # rpc服务器地址, 请按照实际地址修改


def get_client():
    client = zerorpc.Client()
    client.connect(server)  # 连接到rpc服务器
    return client


class RPC(dict):
    """
    提供验证token的服务的类
    定制的返回体
    """

    def __bool__(self):
        if self.get("message") == "success":
            return True
        else:
            return False

    def to_json(self) -> str:
        """转换成json格式"""
        return json.dumps({k: v for k, v in self.items()})

    def get_event(self):
        return self.pop("event", None)

    @classmethod
    def before(cls, req: object):
        """记录用户操作的入日志,这是个快捷方式"""
        return cls.check_request(req)

    def after(self, response: (dict, str), to_json: bool = True) -> (str, dict):
        """记录用户操作的出日志,这是个快捷方式"""
        return self.record_response(response, to_json)

    def record_response(self, response: (dict, Response), to_json: bool = False) -> (str, dict):
        """
        记录返回结果
        :param response: 函数运行的返回体.必须是字典或者json.
        :param to_json: 是否将返回值转换为json. 对django此参数无效
        :return: json
        """
        event = self.get_event()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        if event is None:
            ms = "authorization 验证未通过,不建议继续进行处理"
            raise RuntimeError(ms)
        else:
            if isinstance(response, dict):
                response = to_flat_dict(response)
                status_code = 200
                event['status_code'] = status_code
                response['new_authorization'] = event['new_authorization']
                event['response'] = response
                event['exit_time'] = now
                c = get_client()  # 连接到rpc服务器
                try:
                    c.save(event)
                except Exception as error:
                    error_str = str(error)
                    e2 = {
                        "error": error_str,
                        "file": __file__,
                        "func": sys._getframe().f_code.co_name,
                        "time": now
                    }
                    c.record_error(e2)
                finally:
                    c.close()
                    return json.dumps(response) if to_json else response
            elif isinstance(response, (Response, HttpResponseRedirect)):
                """
                django的rest_framework的响应对象
                """
                status_code = response.status_code
                event['status_code'] = status_code

                if status_code >= 400:
                    data = dict() if response.data is None else response.data  # response的容器
                    data['message'] = "not found object"
                    data['new_authorization'] = event['new_authorization']
                    event['response'] = data
                    response.data = data
                elif 300 <= status_code < 400:
                    data = dict()
                    event['redirect'] = response.url if hasattr(response, "url") else ""
                else:
                    data = dict() if response.data is None else response.data  # response的容器
                    data['new_authorization'] = event['new_authorization']
                    event['response'] = data
                    response.data = data
                event['exit_time'] = now
                c = get_client()  # 连接到rpc服务器
                try:
                    c.save(event)
                except Exception as error:
                    error_str = str(error)
                    data['message'] = error_str
                    e2 = {
                        "error": error_str,
                        "file": __file__,
                        "func": sys._getframe().f_code.co_name,
                        "time": now
                    }
                    c.record_error(e2)
                finally:
                    c.close()
                    return response
            else:
                ms = "response参数必须是字典,json或者Response对象"
                raise TypeError(ms)

    @classmethod
    def check_request(cls, req: object):
        """记录用户操作的入日志"""
        resp = RPC(message="success")
        init = {
            "ip": "",
            "enter_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "user_agent": "",
            "user_id": 0,
            "host": "",
            "path": "",
            "method": "",
            "web_framework": "",
            "get_args": dict(),
            "post_args": dict(),
            "json_args": dict(),
        }
        if isinstance(req, LocalProxy):
            """flask请求"""
            init['web_framework'] = "flask"
            init['ip'] = get_real_ip(req=req)
            init['host'] = req.host
            path = req.path
            init['path'] = path
            init['user_agent'] = req.headers.get("user_agent")
            authorization = req.headers.get("authorization")
            init['user_id'] = 0
            if authorization is None:
                resp['message'] = "authorization not exists"
            else:
                init['authorization'] = authorization
                validate_result = dict()
                c = get_client()  # 连接到rpc服务器
                try:
                    validate_result = c.check_auth(authorization, reduce_url(path))
                except Exception as error:
                    print(error)
                    e2 = {
                        "error": str(error),
                        "file": __file__,
                        "func": sys._getframe().f_code.co_name
                    }
                    c.record_error(e2)
                finally:
                    c.close()
                    user_info = validate_result.get("user_info")
                    if isinstance(user_info, dict):
                        """authorization正确"""
                        new_authorization = validate_result['new_authorization']
                        resp['user_info'] = user_info
                        resp['new_authorization'] = new_authorization
                        init.update(user_info)
                        init['new_authorization'] = new_authorization
                    else:
                        resp['message'] = "authorization invalid"
                        init['message'] = "authorization invalid"
            init['method'] = req.method.lower()
            init['get_args'] = {k: v for k, v in req.args.items()}
            init['post_args'] = {k: v for k, v in req.form.items()}
            init['json_args'] = dict() if req.json is None else req.json

        elif isinstance(req, (HttpRequest, Request)):
            """django的请求"""
            ip = req.META['HTTP_X_FORWARDED_FOR'] if req.META.get('HTTP_X_FORWARDED_FOR') else req.META['REMOTE_ADDR']
            user_agent = req.META['HTTP_USER_AGENT']
            authorization = req.META.get('HTTP_AUTHORIZATION')  # 可能是None
            path = req.path
            get_args = req.GET.dict()
            method = req.method.lower()
            post_args = req.POST.dict()
            # 下方代码为了解决dispatch()的问题
            try:
                json_args = req.data
            except:
                json_args = str(req.body, encoding='utf-8')
            init['web_framework'] = "django"
            init['ip'] = ip
            init['user_agent'] = user_agent
            init['user_id'] = 0
            if authorization is None:
                resp['message'] = "authorization not exists"
            else:
                init['authorization'] = authorization
                validate_result = dict()
                c = get_client()  # 连接到rpc服务器
                try:
                    validate_result = c.check_auth(authorization, reduce_url(path))
                except Exception as error:
                    e2 = {
                        "error": str(error),
                        "file": __file__,
                        "func": sys._getframe().f_code.co_name
                    }
                    c.record_error(e2)
                finally:
                    c.close()
                    user_info = validate_result.get("user_info")
                    if isinstance(user_info, dict):
                        """authorization正确"""
                        new_authorization = validate_result['new_authorization']
                        resp['user_info'] = user_info
                        resp['new_authorization'] = new_authorization
                        init.update(user_info)
                        init['new_authorization'] = new_authorization
                    else:
                        resp['message'] = init['validate_error'] = validate_result.get("message",
                                                                                       "authorization invalid")
                        # init['validate_error'] = "authorization invalid"
            init['host'] = req.get_host()
            init['path'] = path
            init['method'] = method
            init['get_args'] = get_args
            init['post_args'] = post_args
            init['json_args'] = json_args
        else:
            web_framework = req.__class__.__name__
            ms = "未意料的web框架类型: {}".format(web_framework)
            resp['message'] = ms

        message = resp['message']
        if message == "success":
            resp['event'] = init  # 记录的事件信息
        else:
            init['validate_error'] = message
            """authorization验证未通过,直接记录"""
            c = get_client()  # 连接到rpc服务器
            try:
                c.save(init)
            except Exception as error:
                e2 = {
                    "error": str(error),
                    "file": __file__,
                    "func": sys._getframe().f_code.co_name
                }
                c.record_error(e2)
            finally:
                c.close()
                pass
        return resp

    @staticmethod
    def reg_rule(url: str, name: str, level: int = 0, desc: str = "", force: bool = False) -> dict:
        """
        注册路由/权限规则
        注意api_url的命令应该符合规范, 包含版本号,但是不含对象id.
        /v1/common/employee/role_info    (定义一个查看角色信息的权限)  正确
        /v1/common/employee/role_info/2/    (定义一个查看角色信息的权限其中2是角色id)  错误,不要包含对象id
        :param url:    接口的api_url, 请按照四段式命令
        :param name:   接口的名字
        :param level:   控制级别,默认0,0只能系统管理员才能设定的选先,1是集团管理员可设定的, 2 是酒店管理员可设定的
        :param desc:  说明, 默认控制字符
        :param force:  如果存在同名(url相同)的规则, 是否覆盖?False的话,会返回报错信息
        :return: {"message":"success"}或者{"message": "重复的url...."}
        """
        c = get_client()
        res = c.reg_rule(url, name, level, desc, force)
        c.close()
        return res


def get_real_ip(req):
    """
    获取当前请求的真实ip。参数只有一个：
    1.req  当前的请求。一般都是传入当前上下文的request
    return ip地址(字符串格式)
    注意，如果前端的反向代理服务器是nginx的话，需要在配置文件中加上几句。
    在location / 配置下面的proxy_pass   http://127.0.0.1:5666; 后面加上
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    然后才可以用headers["X-Forwarded-For"]取真实ip
    虽然只加proxy_set_header X-Real-IP $remote_addr;这一句的话。
    也可以用request.headers["X-Real-IP"]获取。
    但为了和IIS的兼容性。还是需要再加一句
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    参数
    :parm req: flask 是request对象，
    tornado是 tornado.web.RequestHandler.request或者tornado.websocket.WebSocketHandler.reuest
    """
    try:
        ip = req.headers["X-Forwarded-For"].split(":")[0]
    except KeyError as e:
        ip = req.remote_addr  # 注意：tornado是 request.remote_ip   flask是 req.remote_addr
    if ip.find(",") != -1:
        """处理微信登录时转发的双ip"""
        ip = ip.split(",")[0]
    return ip


def other_can_json(obj):
    """
    把其他对象转换成可json,是to_flat_dict的内部函数
    v = v.strftime("%F %H:%M:%S.%f")是v = v.strftime("%Y-%m-%d %H:%M:%S")的
    简化写法，其中%f是指毫秒， %F等价于%Y-%m-%d.
    注意，这个%F只可以用在strftime方法中，而不能用在strptime方法中
    """
    if isinstance(obj, datetime.datetime):
        if obj.hour == 0 and obj.minute == 0 and obj.second == 0 and obj.microsecond == 0:
            return obj.strftime("%F")
        else:
            return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, datetime.date):
        return obj.strftime("%F")
    elif isinstance(obj, list):
        return [other_can_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: other_can_json(v) for k, v in obj.items()}
    else:
        return obj


def to_flat_dict(a_dict, ignore_columns: list = list()) -> dict:
    """
    转换成可以json的字典,这是一个独立的方法
    :param a_dict: 待处理的doc.
    :param ignore_columns: 不需要返回的列
    :return:
    """
    return {other_can_json(k): other_can_json(v) for k, v in a_dict.items() if k not in ignore_columns}


def reduce_url(url: str) -> str:
    """
    化简接口路径,按照标准重新拼接.
    避免id的干扰.
    :param url:  path不包含?以后的部分
    :return: 处理后的url.
    """
    temp = [x for x in url.split("/") if x.strip() != ""]
    last = temp[-1]
    try:
        int(last)
        temp.pop(-1)
    except Exception as e:
        pass
    finally:
        new_url = "/".join(temp)
        result = "/{}".format(new_url)
        return result


class RPCCommon:
    def __init__(self, server: str, data: dict, func_name: str):
        self.server = server
        self.data = data
        self.func_name = func_name

    def __enter__(self):
        client = zerorpc.Client()
        client.connect(self.server)  # 连接到rpc服务器
        self.client = client
        return self.run()

    def run(self):
        handler = getattr(self.client, self.func_name)
        return handler(self.data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


if __name__ == '__main__':
    pass
