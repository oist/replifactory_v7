# Import the required modules
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, Namespace, join_room, disconnect
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

# Create the app and the socketio instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a long and random string'
app.config['JWT_SECRET_KEY'] = 'another long and random string'
socketio = SocketIO(app)
jwt = JWTManager(app)

# Define a user class and a user database
class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

users = {
    "user1": User("user1", "pass1"),
    "user2": User("user2", "pass2")
}

# Define a custom namespace class that handles socketio events
class MyNamespace(Namespace):
    @jwt_required()
    def on_connect(self):
        # Get the current user from the jwt token
        current_user = get_jwt_identity()
        print(f"User {current_user} connected")

    @jwt_required()
    def on_join(self, data):
        # Join a room specified by the client
        room = data.get('room')
        if room:
            join_room(room)
            print(f"User {current_user} joined room {room}")

# Register the namespace with the socketio instance
socketio.on_namespace(MyNamespace('/my-namespace'))

# Define a login route that returns a jwt token
@app.route('/login', methods=['POST'])
def login():
    # Get the username and password from the request body
    username = request.json.get('username')
    password = request.json.get('password')
    # Validate the credentials
    user = users.get(username)
    if not user or not user.verify_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401
    # Generate an access token
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

# Run the app
if __name__ == '__main__':
    socketio.run(app)