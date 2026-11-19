func TestCopy(t *testing.T) {
	dir := t.TempDir()                       // never real paths
	…
	a := actiontest.New(t, copyDefinition, map[string]any{"source": src, "target": dst})
	res, logs, err := actiontest.Execute(context.Background(), a)
	…
}

func TestCopyConfig(t *testing.T) {
	actiontest.ConfigError(t, copyDefinition, nil, `missing required field "source"`)
}
