from chalice import Blueprint, Response
import chalicelib.credentials as credentials
import boto3
from uuid import uuid4
import chalicelib.connections.user_table as user_table
import chalicelib.connections.music_table as music_table
import chalicelib.connections.sns as sns


api = Blueprint(__name__)


@api.route('/users', methods=['POST'])
def post_user():
    request = api.current_request
    req_obj = request.json_body

    table = user_table.get_or_create_table()
    response = table.put_item(Item=req_obj)

    return response


@api.route('/users/{username}')
def get_user(username):
    table = user_table.get_or_create_table()

    response = table.get_item(Key={'username': username})
    
    if "Item" in response.keys():
        return response["Item"]
    else:
        return {}


@api.route('/users')
def list_users():
    table = user_table.get_or_create_table()

    response = table.scan()
    items = response['Items']

    return items


@api.route('/users', methods=['PUT'])
def update_user():
    request = api.current_request
    req_obj = request.json_body

    table = user_table.get_or_create_table()
    
    username = req_obj['username']
    update_dict = req_obj['update']
    for key in update_dict.keys():
        table.update_item(
            Key={
                'username': username
            },
            UpdateExpression=f'SET {key} = :val1',
            ExpressionAttributeValues={
                ':val1': update_dict[key]
            }
        )

    return Response(body={'status': 'OK', 'updated_keys': list(update_dict.keys())})


@api.route('/users/{username}', methods=['DELETE'])
def delete_user(username):
    table = user_table.get_or_create_table()
    response = table.delete_item(Key={'username': username})

    return response