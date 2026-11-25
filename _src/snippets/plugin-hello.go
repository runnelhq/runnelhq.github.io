package main

import (
	"context"
	"fmt"

	runnel "github.com/runnelhq/sdk-go"
)

type greetConfig struct {
	Name  string `json:"name" doc:"Whom to greet" schema:"required,example=World"`
	Shout bool   `json:"shout" doc:"Capital letters"`
}

func main() {
	p := runnel.New("hello", "1.0.0") // name and version as in plugin.yaml
	runnel.AddAction(p, runnel.Action[greetConfig]{
		Type:        "hello.greet",
		Label:       "Greet",
		Description: "Returns a greeting for a name",
		Run: func(ctx context.Context, call *runnel.Call, c greetConfig) (any, error) {
			call.Log.Info("greeting %s", c.Name)
			return map[string]any{"message": fmt.Sprintf("Hello, %s!", c.Name)}, nil
		},
	})
	p.Main()
}
