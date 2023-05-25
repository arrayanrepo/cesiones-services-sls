## python
import os


## boto 3
import boto3



def publish_event(message):
    
    try:
        print(f'SEND MESSAGE {message}')
        sns_topic_arc = os.environ.get('SNS_TOPIC_ARN')
        sns = boto3.client('sns')
        topic_arn = sns_topic_arc   
        sns.publish(TopicArn=topic_arn, Message=message)
    except Exception as err:
        print(f"Failed to publish message into {topic_arn} to server {err}")