from django.urls import path, re_path

from . import consumers
#
# websocket_urlpatterns = [
#     re_path(r'api/pms_ws/(?P<models_name>\w+)/$', consumers.MessageConsumer),
# ]
#
#
#
# # # from channels.routing import URLRouter, ProtocolTypeRouter
# # from channels.routing import ProtocolTypeRouter, URLRouter
# # from channels.security.websocket import AllowedHostsOriginValidator
# #
# # # My Stuff
# # import backend.routing
# # from .auth_middleware import QueryAuthMiddleware
# # application = ProtocolTypeRouter({
# #     'websocket': AllowedHostsOriginValidator(
# #         QueryAuthMiddleware(
# #             URLRouter(
# #                 backend.routing.websocket_urlpatterns
# #             )
# #         ),
# #     ),
# # })



from django.urls import path
from backend.consumers import MessageConsumer

websocket_urlpatterns = [
    path('ws/chat/', MessageConsumer), # 这里可以定义自己的路由
    # path('ws/<str:username>/',MessagesConsumer) # 如果是传参的路由在连接中获取关键字参数方法：self.scope['url_route']['kwargs']['username']
]
