runnel.AddAction(p, runnel.Action[greetConfig]{
	Type: "hello.greet", Label: "Greet", Description: "Returns a greeting for a name",
	Reference: runnel.Reference{
		Outputs: []runnel.OutputField{
			{Name: "output.message", Type: "string", Description: "The greeting, e.g. Hello, World!"},
			{Name: "output.length", Type: "integer", Description: "Number of bytes of the greeting"},
		},
		Errors: "Fails when name is empty.",
	},
	Run: …,
})

// optional: same rules as the contract tests of Runnel
func TestReference(t *testing.T) { runneltest.CheckReference(t, newPlugin()) }
