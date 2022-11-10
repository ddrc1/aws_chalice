from chalice import Blueprint, Response
import boto3
import chalicelib.credentials as credentials
from chalicelib.requests.music_requests import get_music
from chalicelib.requests.user_requests import get_user

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb', aws_access_key_id=credentials.aws_access_key_id, aws_secret_access_key=credentials.aws_secret_access_key)
sns = boto3.client('sns', aws_access_key_id=credentials.aws_access_key_id, aws_secret_access_key=credentials.aws_secret_access_key)

def send_message(playlist: dict, music: dict, keyword="adicionada"):
    message = f"A música {music['music_name']} do artista {music['artist']} acabou de ser {keyword} na playlist {playlist['playlist_name']}"
    response = sns.publish(TopicArn="arn:aws:sns:us-east-1:952799814065:test", Message=message)
    print(message)
    return response
    

def subscription(playlist: dict, user: dict):
    response = sns.subscribe(TopicArn=playlist['topicArn'], Protocol='email', Endpoint=user['email'], ReturnSubscriptionArn=True)
    return response


def create_topic(name: str):
    response = sns.create_topic(Name=name)
    topicArn = response['TopicArn']
    print("Topic created:", topicArn)
    return topicArn


def get_or_create_table():
    try:
        table = dynamodb.create_table(
            TableName='Playlists',
            KeySchema=[{
                        'AttributeName': 'playlist_name',
                        'KeyType': 'HASH'
                    }],
            AttributeDefinitions=[
                {
                    'AttributeName': 'playlist_name',
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
        table = dynamodb.Table('Playlists')

    return table

table = get_or_create_table()


@api.route('/playlist', methods=['POST'])
def post_musics():
    request = api.current_request
    req_obj = request.json_body

    topicArn = create_topic(req_obj['playlist_name'])
    req_obj['topicArn'] = topicArn

    req_obj['musics'] = []

    response = table.put_item(Item=req_obj)

    return response


@api.route('/playlist/{playlist_name}')
def get_playlist(playlist_name):
    response = table.get_item(Key={'playlist_name': playlist_name})
    item = response['Item']
    return item


@api.route('/list_playlist')
def list_playlist():
    response = table.scan()
    items = response['Items']

    return items


@api.route('/playlist', methods=['PUT'])
def update_music():
    request = api.current_request
    req_obj = request.json_body
    
    playlist_name = req_obj['playlist_name']
    update_dict = req_obj['update']
    for key in update_dict.keys():
        if key == "add" or key == "remove":
            playlist = get_playlist(playlist_name)
            music = get_music(update_dict[key])

            if key == "add" and music not in playlist['musics']:
                table.update_item(
                    Key={
                        'playlist_name': playlist_name
                    },
                    UpdateExpression=f'SET musics = list_append(musics, :val1)',
                    ExpressionAttributeValues={
                        ':val1': [update_dict[key]]
                    }
                )

                send_message(playlist, music, keyword="adicionada")
            elif key == "remove" and music in playlist['musics']:
                playlist = get_playlist(playlist_id)
                musics = playlist['musics']
                index = musics.index()
                del musics[index]

                table.update_item(
                    Key={
                        'ID': playlist_id
                    },
                    UpdateExpression=f'SET musics = :val1',
                    ExpressionAttributeValues={
                        ':val1': musics
                    }
                )

                send_message(playlist, music, keyword="removida")
        else:
            table.update_item(
                Key={
                    'ID': playlist_id
                },
                UpdateExpression=f'SET {key} = :val1',
                ExpressionAttributeValues={
                    ':val1': update_dict[key]
                }
            )

    return Response(body={'status': 'OK', 'updated_keys': list(update_dict.keys())})


@api.route('/playlist/{playlist_name}', methods=['DELETE'])
def delete_playlist(playlist_name):
    response = table.delete_item(Key={'playlist_name': playlist_name})

    return response


@api.route('/playlist/subscribe/{playlist_name}/{username}', methods=['GET'])
def subscribe_playlist(playlist_name, username):
    playlist = get_playlist(playlist_name)
    user = get_user(username)

    response = subscription(playlist, user)

    return response