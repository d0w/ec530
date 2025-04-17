# publisher.py
import paho.mqtt.client as mqtt
import time
import random

broker = "localhost"
topic = "home/temperature/livingroom"

client = mqtt.Client("TemperatureSensor1")
client.connect(broker)

while True:
    temperature = round(random.uniform(20.0, 25.0), 2)
    client.publish(topic, f"{temperature}")
    print(f"Published: {temperature}°C to topic {topic}")
    time.sleep(5)


# subscriber.py
import paho.mqtt.client as mqtt

broker = "localhost"
topic = "home/temperature/livingroom"


def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()}°C on topic {message.topic}")


client = mqtt.Client("HVACController")
client.connect(broker)
client.subscribe(topic)
client.on_message = on_message
client.loop_forever()
