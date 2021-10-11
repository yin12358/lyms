# # from channels.routing import URLRouter, ProtocolTypeRouter
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator
#
# # My Stuff
# import backend.routing
# from auth_middleware import QueryAuthMiddleware
#
# application = ProtocolTypeRouter({
#     'websocket': AllowedHostsOriginValidator(
#         QueryAuthMiddleware(
#             URLRouter(
#                 backend.routing.websocket_urlpatterns
#             )
#         ),
#     ),
# })


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import backend.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            backend.routing.websocket_urlpatterns
        )
    ),
})
