import zerorpc
from django.db import close_old_connections
from django.conf import settings

# My Stuff
# from backend.base_app.rpc_client import get_client
from backend.rpc_client import get_client

server = settings.AUTHORIZATION_RPC_CLIENT  # rpc服务器地址, 请按照实际地址修改


class QueryAuthMiddleware:
    """
    QueryAuthMiddleware authorization
    自定义身份信息验证，项目中前端传递authorization
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        # 确保不会泄漏空闲的数据库连接
        close_old_connections()
        try:
            c = get_client()
            authorization = {info.split("=")[0]: info.split("=")[1]
                             for info in scope['query_string'].decode("utf-8").split("&")}.get("authorization", "")
            result = c.check_auth(authorization, scope['path'])
            if result['message'] == "success":
                scope['user_info'] = result['user_info']
                print(scope)
                return self.inner(scope)
            else:
                return {'message': '认证失败'}
        except Exception as e:
            raise ValueError(
                "AuthMiddleware cannot find session in scope. SessionMiddleware must be above it."
            )
