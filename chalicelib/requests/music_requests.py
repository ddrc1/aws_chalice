from chalice import Blueprint, Response
import boto3
from uuid import uuid4
import chalicelib.credentials as credentials

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb', aws_access_key_id=credentials.aws_access_key_id, aws_secret_access_key=credentials.aws_secret_access_key)

def get_or_create_table():
    try:
        table = dynamodb.create_table(
            TableName='Musics',
            KeySchema=[{
                        'AttributeName': 'ID',
                        'KeyType': 'HASH'
                    }],
            AttributeDefinitions=[
                {
                    'AttributeName': 'ID',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print('Creating table')
        table.wait_until_exists()

    except Exception:
        print("Table exists")
        table = dynamodb.Table('Musics')

    return table

table = get_or_create_table()

@api.route('/music', methods=['POST'])
def post_musics():
    request = api.current_request
    req_obj = request.json_body

    uuid = str(uuid4())
    req_obj['ID'] = uuid

    response = table.put_item(Item=req_obj)

    return response


@api.route('/music/{music_id}')
def get_music(music_id):
    response = table.get_item(Key={'ID': music_id})
    item = response['Item']
    return item


@api.route('/list_music')
def list_music():
    response = table.scan()
    items = response['Items']

    return items


@api.route('/music', methods=['PUT'])
def update_music():
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


@api.route('/music/{music_id}', methods=['DELETE'])
def delete_music(music_id):
    response = table.delete_item(Key={'ID': music_id})

    return response