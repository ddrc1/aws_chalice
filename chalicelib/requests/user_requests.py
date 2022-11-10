from chalice import Blueprint
import boto3
from uuid import uuid4

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb')

def get_or_create_table():
    try:
        table = dynamodb.create_table(
            TableName='Users',
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
        table = dynamodb.Table('Users')

    return table

table = get_or_create_table()

# @api.route('/users/{username}', methods=['GET'])
# def get_user(username):
#     response = table.get_item(Key={'username': username})
#     item = response['Item']
#     return item

@api.route('/users', methods=['GET'])
def get_all_users():
    response = table.scan()#(TableName='Users', IndexName='username')
    items = response['Items']
    return items

@api.route('/users', methods=['POST'])
def post_users():
    uuid = str(uuid4())
    request = api.current_request
    req_obj = request.json_body
    req_obj['id'] = uuid
    response = table.put_item(Item=req_obj)
    return response

@api.route('/users/{id}', methods=['DELETE'])
def update_users(id):
    response = table.delete_item(Key={'id': id})
    return response
