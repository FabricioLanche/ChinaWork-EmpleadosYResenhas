import boto3, json, uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
tabla_resenas = dynamodb.Table('Resenas')

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    body = json.loads(event['body'])
    required = ['local_id', 'pedido_id', 'calificacion', 'resena',
                'cocinero_dni', 'despachador_dni', 'repartidor_dni']
    
    for field in required:
        if field not in body:
            return {'statusCode': 400, 'body': json.dumps({'error': f"Falta el campo {field}"})}
    
    empleados = [
        ('Cocinero', body['cocinero_dni']),
        ('Despachador', body['despachador_dni']),
        ('Repartidor', body['repartidor_dni'])
    ]
    
    items_creados = []
    for rol, dni in empleados:
        pk = f"LOCAL#{body['local_id']}#EMP#{dni}"
        item = {
            'pk': pk,
            'resena_id': str(uuid.uuid4()),
            'local_id': body['local_id'],
            'empleado_dni': dni,
            'rol': rol,
            'pedido_id': body['pedido_id'],
            'resena': body['resena'],
            'calificacion': body['calificacion']
        }
        tabla_resenas.put_item(Item=item)
        items_creados.append(item)

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Reseñas registradas para los empleados del pedido', 'resenas': items_creados}, cls=DecimalEncoder)
    }
