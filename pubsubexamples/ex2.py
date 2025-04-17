import asyncio
import random
import time


# Define a message structure
class Message:
    def __init__(self, topic: str, data: str):
        self.topic = topic
        self.data = data


# Pub/Sub Broker
class Broker:
    def __init__(self):
        self.subscribers = {}  # topic -> list of queues

    def subscribe(self, topic: str):
        queue = asyncio.Queue()
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(queue)
        return queue

    async def publish(self, message: Message):
        queues = self.subscribers.get(message.topic, [])
        for queue in queues:
            await queue.put(message)


# Publisher: Simulates an IoT temperature sensor
async def temperature_sensor(broker: Broker, location: str):
    while True:
        temp = round(random.uniform(20.0, 30.0), 2)
        msg = Message(topic=f"temperature/{location}", data=f"{temp}°C")
        await broker.publish(msg)
        await asyncio.sleep(random.uniform(0.5, 2.0))  # simulate sensor interval


# Subscriber: Receives temperature updates and processes them
async def dashboard(name: str, queue: asyncio.Queue):
    while True:
        message = await queue.get()
        print(f"[{name}] Received from {message.topic}: {message.data}")


# Run the system
async def main():
    broker = Broker()

    # Subscribers
    office_dashboard = broker.subscribe("temperature/office")
    lab_dashboard = broker.subscribe("temperature/lab")

    await asyncio.gather(
        temperature_sensor(broker, "office"),
        temperature_sensor(broker, "lab"),
        dashboard("Office Dashboard", office_dashboard),
        dashboard("Lab Dashboard", lab_dashboard),
    )


asyncio.run(main())
