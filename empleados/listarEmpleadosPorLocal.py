import boto3, json
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Empleados')

def lambda_handler(event, context):
    local_id = event['pathParameters']['local_id']

    response = table.query(
        KeyConditionExpression=Key('local_id').eq(local_id)
    )

    return {'statusCode': 200, 'body': json.dumps(response['Items'])}
