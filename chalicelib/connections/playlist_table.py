import boto3
import chalicelib.credentials as credentials

dynamodb = boto3.resource('dynamodb', aws_access_key_id=credentials.aws_access_key_id, aws_secret_access_key=credentials.aws_secret_access_key)

def get_or_create_table():
    try:
        table = dynamodb.create_table(
            TableName='Playlists',
            KeySchema=[{
                        'AttributeName': 'playlist_id',
                        'KeyType': 'HASH'
                    }],
            AttributeDefinitions=[
                {
                    'AttributeName': 'playlist_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        print('Creating table')
        table.wait_until_exists()

    except Exception:
        table = dynamodb.Table('Playlists')

    return table