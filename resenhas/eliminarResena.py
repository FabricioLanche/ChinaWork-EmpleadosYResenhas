import boto3, json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChinaWok-Resenas')

def lambda_handler(event, context):
    local_id = event['pathParameters']['local_id']
    empleado_dni = event['pathParameters']['empleado_dni']
    resena_id = event['pathParameters']['resena_id']

    pk = f"LOCAL#{local_id}#EMP#{empleado_dni}"
    table.delete_item(Key={'pk': pk, 'resena_id': resena_id})

    return {'statusCode': 200, 'body': json.dumps({'message': 'Reseña eliminada'})}
