import boto3, json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Resenas')

def lambda_handler(event, context):
    local_id = event['pathParameters']['local_id']
    empleado_dni = event['pathParameters']['empleado_dni']
    resena_id = event['pathParameters']['resena_id']
    body = json.loads(event['body'])

    pk = f"LOCAL#{local_id}#EMP#{empleado_dni}"

    update_expr = []
    expr_vals = {}
    for k, v in body.items():
        if k not in ['resena', 'calificacion']:
            continue
        if k == 'calificacion' and not (0 <= v <= 5):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Calificación fuera de rango'})}
        update_expr.append(f"{k} = :{k}")
        expr_vals[f":{k}"] = v

    if not update_expr:
        return {'statusCode': 400, 'body': json.dumps({'error': 'No hay campos válidos para actualizar'})}

    table.update_item(
        Key={'pk': pk, 'resena_id': resena_id},
        UpdateExpression="SET " + ", ".join(update_expr),
        ExpressionAttributeValues=expr_vals
    )

    return {'statusCode': 200, 'body': json.dumps({'message': 'Reseña actualizada'})}
