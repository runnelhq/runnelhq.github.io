// Init meldet das Schema der ausgegebenen Records und die gelesenen Felder (ADR 0007).
func (t *upper) Init(ic *transform.InitContext) (record.Schema, error) {
	ic.Use(t.Field, "field")            // Pfad innerhalb von with: – für Datei, Zeile, Spalte
	return ic.In.With(t.Field, record.String), nil
}
