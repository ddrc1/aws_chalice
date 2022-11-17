import boto3

sns = boto3.client('sns')
response = sns.create_topic(Name="test1")

print(response)

# response = sns.subscribe(TopicArn="arn:aws:sns:us-east-1:952799814065:test", Protocol='email', Endpoint="danielrotheia@gmail.com", ReturnSubscriptionArn=True)
# print(response)

#sns.publish(TopicArn="arn:aws:sns:us-east-1:952799814065:test", Message="Testando, deu certo!")