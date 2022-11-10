from chalice import Blueprint
import boto3
from uuid import uuid4

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb')

def get_or_create_table():
    try:
        table = dynamodb.create_table(
            TableName='Musics',
            KeySchema=[{
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print('Creating table')
        table.wait_until_exists()

    except Exception:
        table = dynamodb.Table('Musics')

    return table

table = get_or_create_table()

@api.route('/musics', methods=['POST'])
def create_music():
    uuid = str(uuid4())
    request = api.current_request
    req_obj = request.json_body
    req_obj['id'] = uuid
    response = table.put_item(Item=req_obj)
    return response

@api.route('/musics/{music_id}', methods=['GET'])
def get_music(music_id):
    response = table.get_item(Key={'music_id': music_id})
    item = response['Item']
    return item

@api.route('/musics', methods=['GET'])
def get_musics():
    response = table.scan()#(TableName='Users', IndexName='username')
    items = response['Items']
    return items