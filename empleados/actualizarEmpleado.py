import boto3, json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Empleados')

def lambda_handler(event, context):
    local_id = event['pathParameters']['local_id']
    dni = event['pathParameters']['dni']
    body = json.loads(event['body'])

    update_expr = []
    expr_attr_vals = {}
    for key, value in body.items():
        if key not in ['nombre', 'apellido', 'calificacion_prom', 'sueldo', 'role']:
            continue
        update_expr.append(f"{key} = :{key}")
        expr_attr_vals[f":{key}"] = value

    if not update_expr:
        return {'statusCode': 400, 'body': json.dumps({'error': 'No hay campos válidos para actualizar'})}

    table.update_item(
        Key={'local_id': local_id, 'dni': dni},
        UpdateExpression="SET " + ", ".join(update_expr),
        ExpressionAttributeValues=expr_attr_vals
    )

    return {'statusCode': 200, 'body': json.dumps({'message': 'Empleado actualizado'})}
