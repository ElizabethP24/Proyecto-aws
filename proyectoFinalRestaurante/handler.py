import boto3
import json

sqs = boto3.resource('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/232754358893/colaPedidos'
RDS = boto3.client('rds')

# rds settings
rds_host  = "proyectorestaurante-dev-mydb-jbwy7e8ppj9m.cyjxxhhjiblv.us-east-1.rds.amazonaws.com"
user_name = "admin"
password = "admin123"
db_name = "pedidos"



def pedidos(event, context):
    if event['httpMethod'] == 'GET':
        # Obtener el ID del pedido que se solicita
        pedido_id = event['queryStringParameters']['id']
        
        # Buscar el pedido en la base de datos
        response = db_name.get_item(
            Key={
                'id': pedido_id
            }
        )
        
        # Devolver los detalles del pedido como respuesta
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Pedido no encontrado'})
            }
    elif event['httpMethod'] == 'POST':
        # Obtener los datos del pedido del evento
        data = json.loads(event['body'])
        nombre = data['nombre']
        direccion = data['direccion']
        telefono = data['telefono']
        correo = data['correo']
        producto = data['producto']
        cantidad = data['cantidad']
        valor_unidad = data['valor_unidad']
        valor_total = data['valor_total']
        
        # Guardar los datos del pedido en la tabla de pedidos
        db_name.put_item(
            Item={
                'id': str(event['requestContext']['requestId']),
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'correo': correo,
                'producto': producto,
                'cantidad': cantidad,
                'valor_unidad': valor_unidad,
                'valor_total': valor_total
            }
        )
        
        # Enviar notificación por correo electrónico al cliente
        
        to_email = "eliza9924@gmail.com"
        subject = "Detalle de pedido"
        message = "Gracias por su pedido. Detalle del pedido:\n\nProducto: {}\nCantidad: {}\nValor unidad: {}\nValor total: {}".format(producto, cantidad, valor_unidad, valor_total)
        ses_client = boto3.client('ses')
        response = ses_client.send_email(
            Source= 'eliza9924@gmail.com',
            Destination={
                'ToAddresses': [
                    to_email,
                ],
            },
            Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Text': {
                        'Data': message,
                    },
                },
            },
        )
        
        # Agregar el pedido a la cola de mensajes
        queue_url = 'https://sqs.us-east-1.amazonaws.com/232754358893/colaPedidos'
        queue = sqs.Queue(queue_url)        
        queue.send_message(MessageBody=json.dumps({'id': str(event['requestContext']['requestId'])}))
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Pedido recibido'})
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Método HTTP no válido'})
        }


#pedidos en cola
queue = sqs.Queue('https://sqs.us-east-1.amazonaws.com/232754358893/colaPedidos')
s3 = boto3.resource('s3')

def pedidosCola(event, context):
    # Obtener el primer mensaje de la cola
    messages = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=0)
    if len(messages) > 0:
        message = messages[0]
        receipt_handle = message.receipt_handle
        message_body = json.loads(message.body)
        message_id = message_body['id']
        
        # Obtener el pedido de la tabla de pedidos
        response = db_name.get_item(Key={'id': message_id})
        item = response['Item']
        
        # Validar información del cliente
        nombre = item['nombre']
        direccion = item['direccion']
        telefono = item['telefono']
        correo = item['correo']
        if not nombre or not direccion or not telefono or not correo:
            # Enviar notificación por correo electrónico al cliente
            to_email = 'eliza9924@gmail.com'
            subject = "Error en el pedido"
            message = "Lo sentimos, su pedido no pudo ser procesado debido a que hace falta información del cliente. Por favor, verifique sus datos y vuelva a intentarlo."
            ses_client = boto3.client('ses')
            response = ses_client.send_email(
                Source='eliza9924@gmail.com',
                Destination={
                    'ToAddresses': [
                        to_email,
                    ],
                },
                Message={
                    'Subject': {
                        'Data': subject,
                    },
                    'Body': {
                        'Text': {
                            'Data': message,
                        },
                    },
                },
            )
            # Eliminar el mensaje de la cola
            message.delete()
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Error en el pedido'})
            }
        
        # Crear archivo en el bucket de respaldo
        s3_object = s3.Object('bucketpedidos', message_id)
        s3_object.put(Body=json.dumps(item))
        s3_object.delete(ExpiresIn=172800) # Eliminar archivo del bucket después de 2 días
                      
        # Eliminar mensaje de la cola
        message.delete()
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Pedido procesado'})
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'No hay pedidos en la cola'})
        }       
    

