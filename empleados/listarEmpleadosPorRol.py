import boto3, json
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Empleados')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    local_id = event['pathParameters']['local_id']
    role = event['pathParameters']['role']

    response = table.query(
        KeyConditionExpression=Key('local_id').eq(local_id),
        FilterExpression=Attr('role').eq(role)
    )

    return {'statusCode': 200, 'body': json.dumps(response['Items'], cls=DecimalEncoder)}
