from chalice import Blueprint, Response
import chalicelib.credentials as credentials
import boto3

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb', aws_access_key_id=credentials.aws_access_key_id, aws_secret_access_key=credentials.aws_secret_access_key)

def get_or_create_table():
    try:
        table = dynamodb.create_table(
            TableName='Users',
            KeySchema=[{
                        'AttributeName': 'username',
                        'KeyType': 'HASH'
                    }],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
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
        table = dynamodb.Table('Users')

    return table

table = get_or_create_table()

@api.route('/user', methods=['POST'])
def post_users():
    request = api.current_request
    req_obj = request.json_body

    response = table.put_item(Item=req_obj)

    return response


@api.route('/user/{username}')
def get_users(username):
    response = table.get_item(Key={'username': username})
    item = response['Item']

    return item


@api.route('/list_user')
def list_users():
    response = table.scan()
    items = response['Items']

    return items


@api.route('/user', methods=['PUT'])
def update_users():
    request = api.current_request
    req_obj = request.json_body
    
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


@api.route('/user/{username}', methods=['DELETE'])
def delete_users(username):
    response = table.delete_item(Key={'username': username})

    return response