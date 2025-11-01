import boto3, json
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChinaWok-Resenas')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    local_id = event['pathParameters']['local_id']
    empleado_dni = event['pathParameters']['empleado_dni']

    pk = f"LOCAL#{local_id}#EMP#{empleado_dni}"
    response = table.query(KeyConditionExpression=Key('pk').eq(pk))

    return {'statusCode': 200, 'body': json.dumps(response['Items'], cls=DecimalEncoder)}
