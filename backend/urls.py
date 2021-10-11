from django.urls import path
from channels.routing import ProtocolTypeRouter,URLRouter

from . import views

urlpatterns = [
    path(r'testapi/', views.testapi, name='testapi'),
]


# application = ProtocolTypeRouter({
#     'websocket':URLRouter([
#         # 书写websocket路由与视图函数对应关系
#     ])
# })