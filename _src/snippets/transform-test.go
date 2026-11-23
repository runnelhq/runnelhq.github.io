func TestUpper(t *testing.T) {
	tr := transformtest.New(t, upperDefinition, map[string]any{"field": "name"})
	out, logs, err := transformtest.Run(context.Background(), tr, record.New(record.Field{Name: "name", Value: "ada"}))
	…
}
