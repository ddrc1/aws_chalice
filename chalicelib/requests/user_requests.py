from chalice import Blueprint
import boto3

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb')

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

@api.route('/create_user', methods=['POST'])
def post_users():
    request = api.current_request
    req_obj = request.json_body

    response = table.put_item(Item=req_obj)
    return response


@api.route('/get_user/{username}')
def get_users(username):
    response = table.get_item(Key={'username': username})
    item = response['Item']

    return item


@api.route('/list_users')
def get_users():
    response = table.scan()#(TableName='Users', IndexName='username')
    items = response['Items']

    return items


# @api.route('/update_user/')
# def update_users():
#     request = api.current_request
#     req_obj = request.json_body
    
#     response = table.get_item(Key={'username': username})
#     item = response['Item']

#     return item


# @api.route('/users/', methods=['POST', 'GET', 'PUT', 'DELETE'])
# def route_users():
#     request = api.current_request

#     if request.method == 'POST':
#         req_obj = request.json_body

#         response = table.put_item(Item=req_obj)
#         return response

#     elif request.method == 'PUT':
#         req_obj = request.json_body
#         username = req_obj['username']
#         key = req_obj['key']
#         value = req_obj['value']

        # response = table.update_item(
        #     Key={
        #         'username': username
        #     },
        #     UpdateExpression=f'SET {key} = :val1',
        #     ExpressionAttributeValues={
        #         ':val1': value
        #     }
        # )

#         return response
#     elif request.method == 'GET':
#         req_obj = request.json_body
#         username = req_obj['username']

#         response = table.get_item(
#             Key={
#                 'username': username
#             }
#         )
#         item = response['Item']

#         return item

#     elif request.method == 'DELETE':
#         req_obj = request.json_body
#         username = req_obj['username']

#         response = table.delete_item(
#             Key={
#                 'username': username
#             }
#         )

#         return response


