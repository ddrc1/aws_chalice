from chalice import Blueprint, Response
import boto3
from uuid import uuid4
import chalicelib.credentials as credentials
from chalicelib.requests.music_requests import get_music
import chalicelib.connections.playlist_table as playlist_table
from chalicelib.requests.user_requests import get_user
import chalicelib.connections.sns as sns


api = Blueprint(__name__)

@api.route('/users/{username}/playlists/{playlist_id}')
def get_playlist_by_user(username, playlist_id):
    table = playlist_table.get_or_create_table()

    response = table.get_item(Key={'playlist_id': playlist_id})
    if "Item" in response.keys():
        return response["Item"]
    else:
        return {}


@api.route('/users/{username}/playlists')
def list_playlist_by_user(username):
    table = playlist_table.get_or_create_table()

    response = table.scan()
    if "Items" in response.keys():
        playlists = response["Items"]
        playlists = [p for p in playlists if p['owner'] == username]
        return playlists
    else:
        return []


@api.route('/users/{username}/playlists', methods=['POST'])
def create_playlists(username):

    table = playlist_table.get_or_create_table()

    request = api.current_request
    req_obj = request.json_body

    uuid = str(uuid4())
    req_obj['playlist_id'] = uuid

    topicArn = sns.create_topic(uuid)
    req_obj['owner'] = username
    req_obj['topicArn'] = topicArn
    req_obj['musics'] = []
    req_obj['users'] = []
    print(req_obj)

    response = table.put_item(Item=req_obj)

    return response


@api.route('/users/{username}/playlists/{playlist_id}', methods=['PUT'])
def add_music_playlist(username, playlist_id):
    playlist = get_playlist_by_user(username, playlist_id)
    user = get_user(username)

    if playlist is not {} and user is not {}:
        table = playlist_table.get_or_create_table()

        request = api.current_request
        req_obj = request.json_body

        music_id = req_obj["music_id"]
        music = get_music(music_id)
        

        table.update_item(
            Key={
                'playlist_id': playlist["playlist_id"]
            },
            UpdateExpression=f'SET musics = list_append(musics, :val1)',
            ExpressionAttributeValues={
                ':val1': [music_id]
            }
        )
        sns.send_message(playlist, music)
        return Response(body={'status': 'OK'})

    else:
        Response(body={'status': 'ERROR'})


@api.route('/users/{username}/playlists/{playlist_id}/subscribe', methods=['POST'])
def subscribe_on_playlist(username, playlist_id):
    playlist = get_playlist_by_user(username, playlist_id)
    user = get_user(username)

    if playlist is not {} and user is not {}:
        table = playlist_table.get_or_create_table()

        request = api.current_request
        req_obj = request.json_body

        subscribed_user_id = req_obj["user_id"]
        subscribed_user = get_user(subscribed_user_id)

        response = sns.subscription(playlist, user)
        return response
    else:
        Response(body={'status': 'ERROR'})