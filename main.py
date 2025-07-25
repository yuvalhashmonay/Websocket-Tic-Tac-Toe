from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
from string import ascii_uppercase
from tic_tac_toe.game_series import GameSeries
import copy
from functools import partial
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "I am secret key so don't tell anyone 🤫"
socketio = SocketIO(app)  # Use eventlet as async_mode

rooms = {}

# constants
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 15


def generate_unique_code(length):
    while True:
        code = ''.join([random.choice(ascii_uppercase) for _ in range(length)])
        if code not in rooms:
            return code


def setup_join(name, room_code):
    rooms[room_code]['player2_name'] = name
    session['player_number'] = 2
    return room_code


def setup_create(name, single_player_btn):
    room_code = generate_unique_code(4)
    rooms[room_code] = {
        "members": 0,
        "messages": [],
        'player1_name': name,
        'is_single_player': single_player_btn is not False
    }
    session['player_number'] = 1
    return room_code


def validate_home_post_request(name, room_code, join):
    if not name:
        return None, "Please enter a name."
    name = name.strip()
    if not (MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH):
        return None, f"Name length has to be {MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} characters long."

    if join is not False:
        if not room_code:
            return None, "Please enter a room code"
        if room_code not in rooms:
            return None, "Room does not exist"
        if rooms[room_code]['members'] == 2 or rooms[room_code]['is_single_player']:
            return None, "This room already has 2 players"
        if name == rooms[room_code]['player1_name']:
            return None, "This name is taken, place choose another"
        return "join", None
    if name.lower() == "computer": # (when it's create)
        return None, "Cannot choose this name"
    return "create", None  # if it's one of the creates


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        room_code = request.form.get("code")
        # When the key exists in the form, the value is en empty string)
        join = request.form.get("join", False)
        # create = request.form.get("create", False)
        single_player_btn = request.form.get("single_player_btn", False)

        action_to_func = {
            'create': partial(setup_create, name=name, single_player_btn=single_player_btn),
            'join': partial(setup_join, name=name, room_code=room_code),
        }

        action, error = validate_home_post_request(name, room_code, join)
        if error is not None:
            logging.warning(f"Error in validating post request: {error}")
            return render_template("home.html", error=error, code=room_code, name=name,
                                   min_name_length=MIN_NAME_LENGTH, max_name_length=MAX_NAME_LENGTH)
        room_code = action_to_func[action]()
        session["room"] = room_code
        session["name"] = name
        return redirect(url_for("room"))
    return render_template("home.html", min_name_length=MIN_NAME_LENGTH, max_name_length=MAX_NAME_LENGTH)


def get_player_names_in_room(game_series=None):
    """
    If a game series already exists in the room, then we can get the player names from the game series object.
    Otherwise, there's only one player connected and we get their name from the session.
    """
    if game_series:
        return game_series.player1.name, game_series.player2.name
    return (session["name"],)


def get_game_series_data(game_series):
    board = copy.deepcopy(game_series.game.board)
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == game_series.game.available_mark:
                board[i][j] = ''

    return {
        'current_player_name': game_series.game.current_player.name,
        'current_player_number': game_series.game.current_player.number,
        'current_player_mark': game_series.game.current_player.mark,
        'connected_players_names': get_player_names_in_room(game_series),
        'board': board,
        'is_over': game_series.game.is_over,
        'ended_in_tie': game_series.game.is_over and game_series.game.winner is None,
        'winner_name': game_series.game.winner.name if game_series.game.winner is not None else '',
        'score_str': game_series.get_score_str().replace('\n', '   |   ')
    }


@app.route("/room")
def room():
    """
    No need to check if the user who came to this '/room' endpoint doesn't belong to a specific room because the room is
    not part of the endpoint, it's just something we set in the user's session here on the backend, and we only do it if
    the user sent a request that came from the home page.
    """
    room = session.get("room")
    client_name = session.get("name")
    if client_name is None:
        logging.warning(f"The user's name is not saved in the session, probably did not come through the home route.")
        return redirect(url_for("home"))
    if room is None:
        logging.warning(f"User {client_name} does not have a room in the session, probably did not come through the home route.")
        return redirect(url_for("home"))
    if room not in rooms:
        logging.warning(f"User {client_name} is trying to to access room {room} which does not exist.")
        return redirect(url_for("home"))
    if rooms[room]["members"] != 0 and client_name == rooms[room]['player1_name']:
        logging.warning(f"User {client_name} is already in the game room and probably trying to open it in another tab/window.")
        return redirect(url_for("home"))
    return render_template(
        "room.html",
        code=room, messages=rooms[room]["messages"],
        player_number=session['player_number'],
        connected_players_names=get_player_names_in_room()
    )


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)


@socketio.on("turn")
def turn(client_move_data):
    room = session.get("room")
    if room not in rooms:
        return

    game_series = rooms[room]['game_series']
    turn_data = {'player_number': session['player_number'],
                 'move': client_move_data}
    move = game_series.game.turns_validator.get_move(turn_data)
    if move is not None:
        game_series.game.act(move=move)
        emit('game_update', get_game_series_data(game_series), room=room)


@socketio.on("new_game")
def create_new_game():
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    game_series = rooms[room].get('game_series')
    if game_series and game_series.game.is_over:  # could there be no game series?
        game_series.create_new_game()
        emit('game_update', get_game_series_data(game_series), room=room)


@socketio.on("connect")
def connect(auth):
    """
    Reminder:
    Once the client instantiates their socketio object (var socketio = io();) they are connected to the server and a
    connect event is emitted to the server. In the function we decorate with the @socketio.on('connect') event
    listener, we can use join_room to connect the client to a specific room. Even though they are already connected
    to the server in general, joining a room is an additional step that logically groups clients for room-specific
    communication.

    We are not redirecting if a room doesn't exist because that's already done in the room route's function, which is
    triggered when the client enters the room route, i.e., before this "connect" function. We also make sure the room
    exists in this "connect" function, but it's a general function that's triggered for every endpoint that establishes
    a connection with the server. In other endpoints, we might not want to redirect the client if there's no room, or we
    might want to redirect them to a different endpoint than home.
    """

    def ready_to_start_playing():
        return rooms[room]["members"] == 2 or rooms[room]["is_single_player"]

    room = session.get("room")
    name = session.get("name")
    if room is None or name is None:
        return

    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1

    if ready_to_start_playing():
        # number_of_human_players = 1 if rooms[room]["is_single_player"] else 2
        number_of_human_players = rooms[room]["is_single_player"] + 2 * (not rooms[room]["is_single_player"])  # same as above, but without if statement
        # Since we're getting the player name from the session, it will be the name of the first player when the first
        # player connects, and the second player when the second player connects.
        player1_name = rooms[room]['player1_name']
        player2_name = None if rooms[room]["is_single_player"] else name
        game_series = GameSeries(number_of_human_players=number_of_human_players, player1_name=player1_name,
                                 player2_name=player2_name)
        rooms[room]['game_series'] = game_series
        emit('game_update', get_game_series_data(game_series), room=room)


@socketio.on("disconnect")
def disconnect():
    """
    When the user quits the page where the socketio variable was initialized — for example, by navigating away, closing
    the browser tab, or closing the browser entirely — the WebSocket connection (or fallback transport) established by
    the Socket.IO client will be closed. With no more client-server heartbeats, the Socket.IO server detects the lost
    connection. Under the hood, this detection causes the server to internally emit a "disconnect" event, which then
    triggers the corresponding event handler on the server side, which this function picks up due to:
    @socketio.on("disconnect")
    """

    room = session.get("room")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        # If there's one player remaining in the room after another one leaves then it's a game that has already
        # started and can now be closed.
        if rooms[room]["members"] <= 1:
            was_a_single_player_game = rooms[room]["is_single_player"]
            # This will redirect the current user if the disconnect was caused by refreshing (it's an if statement
            # that'll happen right afterward in the room route)
            del rooms[room]
            # We're not redirecting to home cause it won't work. When we refresh, we disconnect and get redirected home,
            # but the next thing that comes is that we're going to the same as page again since we refreshed. so the
            # redirection home is before and we don't get to see it cause the reloading of the current page happens fast
            if not was_a_single_player_game:
                # This will redirect all other users since there's a there's a redirection function on the client side
                # that triggers when an "inactive_room" is received.
                emit('inactive_room', room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
