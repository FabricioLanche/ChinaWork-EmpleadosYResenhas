import boto3, json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Empleados')

def lambda_handler(event, context):
    local_id = event['pathParameters']['local_id']
    dni = event['pathParameters']['dni']

    response = table.get_item(Key={'local_id': local_id, 'dni': dni})

    if 'Item' not in response:
        return {'statusCode': 404, 'body': json.dumps({'error': 'Empleado no encontrado'})}

    return {'statusCode': 200, 'body': json.dumps(response['Item'])}
