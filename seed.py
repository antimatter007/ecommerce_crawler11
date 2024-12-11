import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")
QUEUE_NAME = os.getenv("QUEUE_NAME", "crawl_queue")

def seed_domains(domains):
    credentials = pika.PlainCredentials(RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    for domain in domains:
        url = f"https://{domain}"
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=url.encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        print(f"Seeded URL: {url}")
    
    connection.close()

if __name__ == "__main__":
    initial_domains = ["example1.com", "example2.com", "example3.com"]
    seed_domains(initial_domains)
