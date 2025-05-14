from kafka import KafkaConsumer
import psycopg2
import json

# Kafka Config
KAFKA_TOPIC = "youtube-live-chat"
KAFKA_BROKER = "kafka:9092"

# PostgreSQL Config
DB_HOST = "postgres"
DB_NAME = "kafka_db"
DB_USER = "kafka_user"
DB_PASSWORD = "kafka_pass"

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

# Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Consumer is listening...")

for message in consumer:
    data = message.value
    print(f"Received: {data}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kafka_data (
        id SERIAL PRIMARY KEY,
        message JSONB
    )
    """)
    conn.commit()

    # Insert into PostgreSQL
    cursor.execute("INSERT INTO kafka_data (message) VALUES (%s)", (json.dumps(data),))
    conn.commit()

cursor.close()
conn.close()