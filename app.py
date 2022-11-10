from chalice import Chalice
from chalicelib.requests.user_requests import api as user_api
from chalicelib.requests.music_requests import api as music_api
from chalicelib.requests.playlist_requests import api as playlist_api

app = Chalice(app_name='streamming')
#app.debug = True

app.register_blueprint(user_api)
app.register_blueprint(music_api)
app.register_blueprint(playlist_api)

@app.route('/')
def index():
    return {'response': "It's working!"}
    