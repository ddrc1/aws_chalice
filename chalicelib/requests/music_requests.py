from chalice import Blueprint, Response
import boto3
from uuid import uuid4
import chalicelib.credentials as credentials
import chalicelib.connections.user_table as user_table
import chalicelib.connections.music_table as music_table

api = Blueprint(__name__)


@api.route('/musics', methods=['POST'])
def post_musics():
    request = api.current_request
    req_obj = request.json_body

    uuid = str(uuid4())
    req_obj['ID'] = uuid

    table = music_table.get_or_create_table()
    response = table.put_item(Item=req_obj)

    return response


@api.route('/musics/{music_id}')
def get_music(music_id):
    table = music_table.get_or_create_table()
    response = table.get_item(Key={'ID': music_id})

    item = response['Item']
    return item


@api.route('/musics')
def list_music():
    table = music_table.get_or_create_table()

    response = table.scan()
    items = response['Items']

    return items


@api.route('/musics', methods=['PUT'])
def update_music():
    table = music_table.get_or_create_table()

    request = api.current_request
    req_obj = request.json_body
    
    music_id = req_obj['ID']
    update_dict = req_obj['update']
    for key in update_dict.keys():
        table.update_item(
            Key={
                'ID': music_id
            },
            UpdateExpression=f'SET {key} = :val1',
            ExpressionAttributeValues={
                ':val1': update_dict[key]
            }
        )

    return Response(body={'status': 'OK', 'updated_keys': list(update_dict.keys())})


@api.route('/musics/{music_id}', methods=['DELETE'])
def delete_music(music_id):
    table = music_table.get_or_create_table()
    
    response = table.delete_item(Key={'ID': music_id})

    return response