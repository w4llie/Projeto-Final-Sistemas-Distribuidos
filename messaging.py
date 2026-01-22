import pika
import uuid
import json

class MessageBroker:
    """
    Classe utilitária para comunicação assíncrona via RabbitMQ.
    """
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()

    def publish_async(self, exchange_name, routing_key, message):
        """Publica uma mensagem de forma assíncrona em um 'topic' exchange."""
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        print(f" [x] Enviado para '{exchange_name}' com chave '{routing_key}': {message}")

    def consume_async(self, exchange_name, routing_key, callback):
        """Consome mensagens de forma assíncrona de um 'topic' exchange."""
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

        print(f' [*] Aguardando mensagens assíncronas em {queue_name} (bind: {routing_key}). Para sair, pressione CTRL+C')
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def close(self):
        """Fecha a conexão."""
        self.connection.close()

class RpcClient:
    """
    Cliente para chamadas de procedimento remoto (RPC) via RabbitMQ.
    """
    def __init__(self, host='localhost'):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        """Callback para receber a resposta do servidor RPC."""
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body.decode('utf-8'))

    def call(self, queue_name, message):
        """Envia a requisição RPC e espera pela resposta."""
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(message).encode('utf-8'))
        
        # Espera pela resposta
        while self.response is None:
            self.connection.process_data_events()
        
        return self.response

    def close(self):
        """Fecha a conexão."""
        self.connection.close()

def rpc_server_setup(queue_name, callback):
    """
    Configura um servidor RPC.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    def on_request(ch, method, props, body):
        request_data = json.loads(body.decode('utf-8'))
        print(f" [.] Recebido RPC em '{queue_name}': {request_data}")
        
        response = callback(request_data)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                         body=json.dumps(response).encode('utf-8'))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_request)

    print(f' [*] Aguardando requisições RPC em {queue_name}. Para sair, pressione CTRL+C')
    channel.start_consuming()