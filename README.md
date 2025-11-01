# China Work - Microservicio de Empleados y Reseñas

Microservicio serverless para la gestión de empleados y sus reseñas de desempeño en la cadena de restaurantes China Wok, desplegado en AWS Lambda con API Gateway y DynamoDB.

## Descripción

Este microservicio se encarga exclusivamente de:
- **Gestión de empleados**: CRUD completo (crear, leer, actualizar, eliminar)
- **Gestión de reseñas**: Registro y administración de calificaciones de empleados por pedido
- **Consultas especializadas**: Filtrado de empleados por local y rol
- **Actualización automática de promedios**: Mediante DynamoDB Streams

## Arquitectura

- **Runtime**: Python 3.13
- **Framework**: Serverless Framework
- **Base de datos**: DynamoDB (tablas `Empleados` y `Resenas`)
- **API**: API Gateway con integración Lambda
- **Autenticación**: IAM Role (LabRole)
- **Event Processing**: DynamoDB Streams

## Estructura del Proyecto

```
china-work-analytics/
├── empleados/
│   ├── crearEmpleado.py
│   ├── obtenerEmpleado.py
│   ├── listarEmpleadosPorLocal.py
│   ├── listarEmpleadosPorRol.py
│   ├── actualizarEmpleado.py
│   ├── eliminarEmpleado.py
│   └── __init__.py
├── resenhas/
│   ├── registrarResena.py
│   ├── obtenerResenasPorEmpleado.py
│   ├── actualizarResena.py
│   ├── eliminarResena.py
│   ├── actualizarPromedioEmpleado.py  # Trigger DynamoDB Streams
│   └── __init__.py
├── serverless.yml
├── requirements.txt
├── .env                     # Variables de entorno (NO se sube a Git)
├── .env.example             # Plantilla de variables de entorno
├── .gitignore
└── README.md
```

## Tablas DynamoDB

### Tabla: Empleados
- **Partition Key**: `local_id` (String) - Identificador del local
- **Sort Key**: `dni` (String) - DNI del empleado
- **Atributos**:
  - `nombre`: Nombre del empleado
  - `apellido`: Apellido del empleado
  - `role`: Rol (Cocinero, Despachador, Repartidor)
  - `calificacion_prom`: Promedio de calificaciones (actualizado automáticamente)
  - `sueldo`: Sueldo del empleado

### Tabla: Resenas
- **Partition Key**: `pk` (String) - Formato: `LOCAL#{local_id}#EMP#{dni}`
- **Sort Key**: `resena_id` (String) - UUID único de la reseña
- **DynamoDB Stream**: ✅ Habilitado con tipo "New image"
- **Atributos**:
  - `local_id`: ID del local
  - `empleado_dni`: DNI del empleado
  - `rol`: Rol del empleado en el pedido
  - `pedido_id`: ID del pedido evaluado
  - `resena`: Comentario de la reseña
  - `calificacion`: Calificación de 0 a 5

## DynamoDB Streams - Actualización Automática de Promedios

Este microservicio utiliza **DynamoDB Streams** para actualizar automáticamente el promedio de calificaciones de los empleados.

### ¿Cómo funciona?
1. Cuando se inserta una nueva reseña en la tabla `Resenas`
2. El Stream detecta el cambio y dispara la función Lambda `actualizarPromedioEmpleado`
3. La función consulta todas las reseñas del empleado
4. Calcula el nuevo promedio
5. Actualiza el campo `calificacion_prom` en la tabla `Empleados`

### Configuración del Stream
- **Tipo**: New image (solo captura nuevos registros INSERT)
- **Batch size**: 10 registros por invocación
- **Starting position**: LATEST (procesa solo registros nuevos desde el deploy)
- **ARN**: Configurado mediante variable de entorno `RESENAS_STREAM_ARN`

### Ventajas
✅ Actualización en tiempo real sin intervención manual
✅ Desacoplamiento entre registro de reseñas y cálculo de promedios
✅ Escalable y eficiente
✅ Sin necesidad de lógica adicional en endpoints HTTP

## API Endpoints

### Empleados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/empleados` | Crear nuevo empleado |
| GET | `/empleados/{local_id}/{dni}` | Obtener empleado específico |
| GET | `/empleados/local/{local_id}` | Listar todos los empleados de un local |
| GET | `/empleados/local/{local_id}/rol/{role}` | Listar empleados por local y rol específico |
| PUT | `/empleados/{local_id}/{dni}` | Actualizar información de empleado |
| DELETE | `/empleados/{local_id}/{dni}` | Eliminar empleado |

### Reseñas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/resenas` | Registrar reseña de pedido (crea 3 registros: cocinero, despachador, repartidor) |
| GET | `/resenas/{local_id}/{empleado_dni}` | Obtener todas las reseñas de un empleado |
| PUT | `/resenas/{local_id}/{empleado_dni}/{resena_id}` | Actualizar una reseña específica |
| DELETE | `/resenas/{local_id}/{empleado_dni}/{resena_id}` | Eliminar una reseña específica |

## Instalación y Despliegue

### Requisitos Previos
- Node.js y npm instalados
- Serverless Framework: `npm install -g serverless`
- Credenciales AWS configuradas
- Python 3.13
- Tablas DynamoDB `Empleados` y `Resenas` creadas previamente
- **DynamoDB Stream habilitado en la tabla `Resenas`** (tipo "New image")

### Configuración de Variables de Entorno

Este proyecto utiliza variables de entorno para proteger información sensible como el ARN del DynamoDB Stream.

#### 1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

#### 2. Habilita DynamoDB Stream en tu tabla:
- Ve a **AWS Console** → **DynamoDB** → **Tables** → **Resenas**
- Pestaña **"Exports and streams"**
- Click en **"Enable DynamoDB stream"**
- Selecciona **"New image"**
- Copia el **Stream ARN** generado (ejemplo: `arn:aws:dynamodb:us-east-1:123456789012:table/ChinaWok-Resenas/stream/2025-11-01T12:34:56.789`)

#### 3. Configura el archivo `.env`:
Pega el ARN copiado:
```bash
RESENAS_STREAM_ARN=arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/YOUR_TABLE/stream/TIMESTAMP
```

#### ⚠️ Importante para AWS Academy Learner Lab:
Si usas AWS Academy, el **Account ID** cambiará cada vez que inicies un nuevo laboratorio. Deberás:
1. Obtener el nuevo Stream ARN de la tabla `Resenas`
2. Actualizar el valor en el archivo `.env`
3. Redesplegar con `serverless deploy`

### Pasos para Desplegar

1. **Instalar dependencias de Python**:
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno** (ver sección anterior)

3. **Desplegar el servicio**:
```bash
serverless deploy
```

4. **Verificar el despliegue**:
```bash
serverless info
```

5. **Ver logs de funciones HTTP**:
```bash
serverless logs -f crearEmpleado --tail
```

6. **Ver logs del Stream (actualización de promedios)**:
```bash
serverless logs -f actualizarPromedioEmpleado --tail
```

7. **Eliminar el despliegue**:
```bash
serverless remove
```

## Ejemplos de Uso

### Crear Empleado
```bash
curl -X POST https://your-api-url/empleados \
  -H "Content-Type: application/json" \
  -d '{
    "local_id": "LOCAL001",
    "dni": "12345678",
    "nombre": "Juan",
    "apellido": "Pérez",
    "role": "Cocinero",
    "calificacion_prom": 0,
    "sueldo": 1500
  }'
```

### Obtener Empleado
```bash
curl -X GET https://your-api-url/empleados/LOCAL001/12345678
```

### Listar Empleados por Local
```bash
curl -X GET https://your-api-url/empleados/local/LOCAL001
```

### Registrar Reseña de Pedido
```bash
curl -X POST https://your-api-url/resenas \
  -H "Content-Type: application/json" \
  -d '{
    "local_id": "LOCAL001",
    "pedido_id": "PED123",
    "calificacion": 5,
    "resena": "Excelente servicio",
    "cocinero_dni": "12345678",
    "despachador_dni": "87654321",
    "repartidor_dni": "11223344"
  }'
```

**Nota**: Al registrar una reseña, el Stream automáticamente actualizará el `calificacion_prom` de los 3 empleados involucrados.

### Obtener Reseñas de un Empleado
```bash
curl -X GET https://your-api-url/resenas/LOCAL001/12345678
```

## Validaciones Implementadas

### Empleados
- Campos requeridos: `local_id`, `dni`, `nombre`, `apellido`, `role`
- Calificación promedio: debe estar entre 0 y 5
- Sueldo: no puede ser negativo

### Reseñas
- Campos requeridos: `local_id`, `pedido_id`, `calificacion`, `resena`, `cocinero_dni`, `despachador_dni`, `repartidor_dni`
- Calificación: debe estar entre 0 y 5
- Cada pedido genera 3 reseñas (una por rol: cocinero, despachador, repartidor)


### `.env.example` (se sube a Git)
Plantilla con placeholders para compartir:
```bash
RESENAS_STREAM_ARN=arn:aws:dynamodb:REGION:ACCOUNT_ID:table/TABLE_NAME/stream/TIMESTAMP
```

## Notas Técnicas

- Las funciones Lambda tienen 256MB de memoria y 20 segundos de timeout
- CORS está habilitado en todos los endpoints HTTP
- Se utiliza el rol IAM `LabRole` con permisos preconfigurados para DynamoDB
- Las tablas DynamoDB deben existir previamente al despliegue
- **DynamoDB Streams** debe estar habilitado en la tabla `Resenas` antes del deploy
- Variables sensibles (ARN del Stream) se gestionan mediante archivos `.env`
- El microservicio está diseñado para ser independiente y escalable
- La función `actualizarPromedioEmpleado` se ejecuta de forma asíncrona al registrar reseñas

## Costos de DynamoDB Streams

Los costos de DynamoDB Streams son mínimos:
- **Lectura de Streams**: $0.02 por 100,000 unidades de lectura
- **Invocaciones Lambda**: Incluidas en el free tier (1M invocaciones/mes gratis)
- Para un restaurante con 100 pedidos/día: ~$0.60/mes


## Troubleshooting

### El promedio no se actualiza automáticamente
1. Verifica que el Stream esté habilitado en la tabla `Resenas`
2. Revisa los logs: `serverless logs -f actualizarPromedioEmpleado --tail`
3. Confirma que el ARN en `.env` es correcto
4. Verifica que la función Lambda tenga permisos (rol `LabRole`)

### Error al desplegar
- Si usas AWS Academy, asegúrate de que el Account ID en el ARN coincida con tu laboratorio actual
- Verifica que las tablas existan antes del deploy

