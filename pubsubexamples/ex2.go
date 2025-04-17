
// publisher.go
package main

import (
    "fmt"
    "math/rand"
    "time"

    MQTT "github.com/eclipse/paho.mqtt.golang"
)

func main() {
    opts := MQTT.NewClientOptions().AddBroker("tcp://localhost:1883")
    opts.SetClientID("GoTempSensor")

    client := MQTT.NewClient(opts)
    if token := client.Connect(); token.Wait() && token.Error() != nil {
        panic(token.Error())
    }

    for {
        temp := 20.0 + rand.Float64()*5
        payload := fmt.Sprintf("%.2f", temp)
        token := client.Publish("home/temperature/livingroom", 0, false, payload)
        token.Wait()
        fmt.Println("Published:", payload)
        time.Sleep(5 * time.Second)
    }
}



// subscriber.go
package main

import (
    "fmt"
    MQTT "github.com/eclipse/paho.mqtt.golang"
)

func main() {
    opts := MQTT.NewClientOptions().AddBroker("tcp://localhost:1883")
    opts.SetClientID("GoHVACController")

    messageHandler := func(client MQTT.Client, msg MQTT.Message) {
        fmt.Printf("Received: %s°C from topic: %s\n", msg.Payload(), msg.Topic())
    }

    client := MQTT.NewClient(opts)
    if token := client.Connect(); token.Wait() && token.Error() != nil {
        panic(token.Error())
    }

    client.Subscribe("home/temperature/livingroom", 0, messageHandler)
    select {} // keep the subscriber running
}
