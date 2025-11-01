import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
tabla_resenas = dynamodb.Table('Resenas')
tabla_empleados = dynamodb.Table('Empleados')

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue

        item = record['dynamodb']['NewImage']
        local_id = item['local_id']['S']
        empleado_dni = item['empleado_dni']['S']
        pk = f"LOCAL#{local_id}#EMP#{empleado_dni}"

        # 1️⃣ Consultar todas las reseñas del empleado
        response = tabla_resenas.query(KeyConditionExpression=Key('pk').eq(pk))
        items = response['Items']
        if not items:
            continue

        # 2️⃣ Calcular nuevo promedio
        total = sum(float(i['calificacion']) for i in items)
        promedio = round(total / len(items), 2)

        # 3️⃣ Actualizar calificacion_prom en tabla Empleados
        tabla_empleados.update_item(
            Key={'local_id': local_id, 'dni': empleado_dni},
            UpdateExpression="SET calificacion_prom = :p",
            ExpressionAttributeValues={':p': promedio}
        )

    return {'statusCode': 200, 'body': 'Promedios actualizados correctamente'}
