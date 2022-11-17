import boto3
import chalicelib.credentials as credentials

sns = boto3.client('sns', aws_access_key_id=credentials.aws_access_key_id, aws_secret_access_key=credentials.aws_secret_access_key)

def send_message(playlist: dict, music: dict):
    message = f"A música {music['music_name']} do artista {music['artist']} acabou de ser adicionada na playlist {playlist['playlist_id']}"
    response = sns.publish(TopicArn=playlist['topicArn'], Message=message)
    return response
    

def subscription(playlist: dict, user: dict):
    response = sns.subscribe(TopicArn=playlist['topicArn'], Protocol='email', Endpoint=user['email'], ReturnSubscriptionArn=True)
    return response


def create_topic(name: str):
    response = sns.create_topic(Name=name)
    topicArn = response['TopicArn']
    print("Topic created:", topicArn)
    return topicArn