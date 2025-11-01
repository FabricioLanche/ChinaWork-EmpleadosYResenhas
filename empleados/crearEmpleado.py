import boto3, json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChinaWok-Empleados')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    body = json.loads(event['body'])

    required = ["local_id", "dni", "nombre", "apellido", "role"]
    for field in required:
        if field not in body:
            return {'statusCode': 400, 'body': json.dumps({'error': f"Falta el campo requerido: {field}"})}

    # Validaciones básicas
    calificacion = body.get('calificacion_prom', 0)
    if not (0 <= calificacion <= 5):
        return {'statusCode': 400, 'body': json.dumps({'error': 'La calificación debe estar entre 0 y 5'})}
    
    sueldo = body.get('sueldo', 0)
    if sueldo < 0:
        return {'statusCode': 400, 'body': json.dumps({'error': 'El sueldo no puede ser negativo'})}

    item = {
        'local_id': body['local_id'],
        'dni': body['dni'],
        'nombre': body['nombre'],
        'apellido': body['apellido'],
        'role': body['role'],
        'calificacion_prom': calificacion,
        'sueldo': sueldo
    }

    table.put_item(Item=item)
    return {'statusCode': 201, 'body': json.dumps({'message': 'Empleado creado', 'empleado': item}, cls=DecimalEncoder)}
