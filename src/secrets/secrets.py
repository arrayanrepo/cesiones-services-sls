## python
import logging

## boto3
import boto3
import base64
import json
from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)-8s %(lineno)d] - (%(module)s.%(funcName)s) %(message)s)')
logger = logging.getLogger(__name__)

def get_secrets(secret: str, region : str):

    secret_name = secret
    region_name = region
    secret = None

    logger.info('init get secrets')
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':

            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':

            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':

            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':

            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':

            raise e
    else:

        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    
    return json.loads(secret)