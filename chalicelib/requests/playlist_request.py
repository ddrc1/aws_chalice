from chalice import Blueprint
import boto3

api = Blueprint(__name__)
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

def send_message(playlist: dict, music: dict):
    message = f"A música {music['ID']} do artista {music["Artista"]} acabou de ser adicionada na playlist {playlist["ID"]}"
    response = sns.publish(TopicArn="arn:aws:sns:us-east-1:952799814065:test", Message="Testando, deu certo!")
    return response
    

def subscription(playlist: dict, user: dict):
    response = sns.subscribe(TopicArn=playlist['topicArn'], Protocol='email', Endpoint=user['email'], ReturnSubscriptionArn=True)
    return response