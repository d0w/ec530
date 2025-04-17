// pubsub.go
package main

import (
	"fmt"
	"math/rand"
	"time"
)

type Broker struct {
	subscribers map[string][]chan float64
}

func NewBroker() *Broker {
	return &Broker{
		subscribers: make(map[string][]chan float64),
	}
}

func (b *Broker) Subscribe(topic string) <-chan float64 {
	ch := make(chan float64)
	b.subscribers[topic] = append(b.subscribers[topic], ch)
	return ch
}

func (b *Broker) Publish(topic string, msg float64) {
	for _, ch := range b.subscribers[topic] {
		go func(c chan float64) {
			c <- msg
		}(ch)
	}
}

func temperatureSensor(b *Broker, topic string) {
	for {
		temp := 20 + rand.Float64()*5
		fmt.Printf("[Sensor] Publishing: %.2f°C\n", temp)
		b.Publish(topic, temp)
		time.Sleep(2 * time.Second)
	}
}

func hvacSystem(ch <-chan float64) {
	for temp := range ch {
		fmt.Printf("[HVAC] Received: %.2f°C\n", temp)
	}
}

func main() {
	broker := NewBroker()
	topic := "home/temperature/livingroom"

	sub := broker.Subscribe(topic)
	go hvacSystem(sub)
	go temperatureSensor(broker, topic)

	select {} // Keep the main goroutine alive
}
