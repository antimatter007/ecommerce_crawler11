import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")
QUEUE_NAME = os.getenv("QUEUE_NAME", "crawl_queue")

class QueueManager:
    def __init__(self):
        credentials = pika.PlainCredentials(RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)
        parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def publish_url(self, url):
        self.channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=url.encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )

    def consume_urls(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
        self.channel.start_consuming()

    def ack_message(self, delivery_tag):
        self.channel.basic_ack(delivery_tag=delivery_tag)
