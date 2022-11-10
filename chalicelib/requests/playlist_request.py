from chalice import Blueprint
import boto3
from uuid import uuid4

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb')
client = boto3.client('dynamodb')
sns = boto3.client('sns')

def get_or_create_table(table_name):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
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
        table = dynamodb.Table(table_name)

    return table

@api.route('/users/{id}/playlists', methods=['GET'])
def get_playlist(id):
    response = client.scan(TableName=id)
    return response

# @api.route('/users/{id}/playlists/{playlist_id}', methods=['GET'])
# def add_music_playlist(id,playlist_id):
    
#     return 

@api.route('/users/{id}/playlists', methods=['POST'])
def create_playlist(id):
    table = get_or_create_table(id)
    uuid = str(uuid4())
    request = api.current_request
    req_obj = request.json_body
    req_obj['id'] = uuid
    response = table.put_item(Item=req_obj)
    return response

    


# def send_message(playlist: dict, music: dict):
#     message = f"A música {music['ID']} do artista {music['Artista']} acabou de ser adicionada na playlist {playlist['ID']}"
#     response = sns.publish(TopicArn="arn:aws:sns:us-east-1:952799814065:test", Message="Testando, deu certo!")
#     return response
    

# def subscription(playlist: dict, user: dict):
#     response = sns.subscribe(TopicArn=playlist['topicArn'], Protocol='email', Endpoint=user['email'], ReturnSubscriptionArn=True)
#     return 