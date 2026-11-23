// Init reports the schema of the emitted records and the fields it reads (ADR 0007).
func (t *upper) Init(ic *transform.InitContext) (record.Schema, error) {
	ic.Use(t.Field, "field")            // path within with: – for file, line, column
	return ic.In.With(t.Field, record.String), nil
}
