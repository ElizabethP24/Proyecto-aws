# Proyecto-aws
Proyecto aws serverless.yml

Implementación de una aplicación de toma de pedidos a domicilio de un restaurante en AWS utilizando Serverless
Introducción

Pasos a seguir
1. Crear una función Lambda (pedidos) para procesar el pedido del cliente
La función Lambda se encargará de recibir la información del pedido del cliente, como el nombre completo, la dirección, el teléfono, el correo electrónico, el producto, la cantidad, el valor unitario y el valor total. 
Esta información se utilizó para enviar una notificación por correo electrónico al cliente con los detalles del pedido.
Además, la función Lambda pasará a la cola el pedido para ser procesado y enviado.

2. Crear una cola SQS para procesar los pedidos
La cola SQS se encargará de recibir los pedidos puestos en cola por la función Lambda y procesarlos para su envío. 
Podemos configurar la cola SQS como desencadenador de la función lambda (pedidosCola) para que envíe una notificación por correo electrónico a los dueños del restaurante cuando haya un nuevo pedido en la cola. 


3. Crear una función Lambda para procesar los pedidos en la cola
La función Lambda se encargará de procesar los pedidos en la cola SQS y enviarlos al cliente. 
Además, la función Lambda guardará una copia de cada pedido en un cubo de respaldo en S3.

4. Cree un API Gateway con dos servicios
El primer servicio debe permitir a los clientes realizar un pedido mediante una solicitud POST.
El segundo servicio debe permitir a los dueños del restaurante buscar un pedido por ID mediante una solicitud GET.

5. Configure un evento programado de AWS Lambda para eliminar los archivos del depósito de respaldo cada 2 días
Podemos configurar un evento programado de Lambda para que se ejecute cada 2 días y eliminar los archivos del depósito de respaldo en S3. 
Esto ayudará a mantener el almacenamiento de datos organizado y reducir el costo de almacenamiento.

6. Crear una base de datos RDS para guardar los datos de los pedidos
La base de datos RDS puede ser configurada para recibir actualizaciones de la función Lambda y mantener los registros actualizados.

7. Crear un balanceador de carga para los pedidos para distribuir la carga de trabajo en la aplicación. 
Se puede configurar el balanceador de carga para manejar la carga de trabajo de la función Lambda, el Serverless, el GET y el POST.

