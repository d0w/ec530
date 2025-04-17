# pubsub.py
import threading
import time
import random
from queue import Queue


class PubSubBroker:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, topic, callback):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    def publish(self, topic, message):
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                callback(message)


# Simulated subscriber
def hvac_system(message):
    print(f"[HVAC] Received temperature: {message}°C")


# Simulated publisher
def temperature_sensor(broker, topic):
    while True:
        temp = round(random.uniform(20.0, 25.0), 2)
        print(f"[Sensor] Publishing temperature: {temp}°C")
        broker.publish(topic, temp)
        time.sleep(2)


if __name__ == "__main__":
    broker = PubSubBroker()
    topic = "home/temperature/livingroom"

    broker.subscribe(topic, hvac_system)

    publisher_thread = threading.Thread(target=temperature_sensor, args=(broker, topic))
    publisher_thread.start()
