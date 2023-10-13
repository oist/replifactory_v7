import logging
from flask import request, current_app
from flask_socketio import SocketIO, Namespace, emit
import jwt

log = logging.getLogger(__name__)
# def authenticate(socket):
#     token = request.headers.get("Authorization")
#     if not token:
#         return False
#     try:
#         decoded_token = jwt.decode(
#             token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
#         )
#         socket.user_id = decoded_token["user_id"]
#         return True
#     except:
#         return False


class MachineNamespace(Namespace):
    def on_connect(self):
        log.debug("socket.io client connected")
        pass
        # if not authenticate(self):
        #     return False
        # Your code here

    def on_disconnect(self):
        log.debug("socket.io client disconnected")
        pass
        # Your code here

    def on_join(self, data):
        # Join a room specified by the client
        room = data.get('room')
        if room:
            # join_room(room)
            print(f"Joined room {room}")

    def on_my_event(self, data):
        pass
        # if not authenticate(self):
        #     return False
        # Your code here