from flask import Flask, request, jsonify
from flask.json import JSONEncoder

app = Flask(__name__)
app.users = {}
app.id_count = 1
app.tweets = []


class CustomJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)


app.json_encoder = CustomJsonEncoder


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'


@app.route('/sign-up', methods=['POST'])
def sign_up():
    new_user = request.json
    new_user['id'] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count += 1

    return jsonify(new_user)


@app.route('/tweet', methods=['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    twwet = payload['tweet']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다.', 400

    if len(twwet) > 10:
        return '10자를 초과하였습니다.', 400

    app.tweets.append({
        'user_id': user_id,
        'tweet': twwet
    })

    return '', 200


@app.route('/follow', methods=['POST'])
def follow():
    payload = request.json
    user_id = int(payload['id'])
    follow_id = int(payload.get('follow'))

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다.', 400

    if follow_id not in app.users:
        return '팔로우 하고자 하는 사용자가 존재하지 않습니다.', 400

    user = app.users.get(user_id)
    user.setdefault('follow', set()).add(follow_id)

    return jsonify(user)


@app.route('/unfollow', methods=['POST'])
def unfollow():
    payload = request.json
    user_id = int(payload['id'])
    unfollow_id = int(payload['unfollow'])

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다.', 400

    if unfollow_id not in app.users:
        return '언 팔로우 하고자 하는 사용자가 존재하지 않습니다.', 400

    user = app.users.get(user_id)
    user.setdefault('follow', set()).discard(unfollow_id)

    return jsonify(user)


@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '사용자가 존재하지 않습니다.', 400

    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    time_line = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

    return jsonify({
        'user_id': user_id,
        'time_line': time_line
    })
