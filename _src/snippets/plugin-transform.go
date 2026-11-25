// greetRecords adds the greeting to every record; records without a name go to the error
// link with _error and _errorField.
func greetRecords(ctx context.Context, s *runnel.Stream, c greetFieldConfig) error {
	c.defaults()
	for {
		b, ok, err := s.Next(ctx)
		if err != nil || !ok {
			return err
		}
		at := b.Fields.Index(c.Field)
		if at < 0 {
			return fmt.Errorf("field %q is not in the records", c.Field)
		}
		out := append(slices.Clone(b.Fields), runnel.Field{Name: c.Target, Type: runnel.TypeString})
		var good, bad [][]any
		for _, row := range b.Rows {
			name, _ := row[at].(string)
			if strings.TrimSpace(name) == "" {
				bad = append(bad, runnel.ErrorRow(row, "name is empty", c.Field))
				continue
			}
			good = append(good, append(row, fmt.Sprintf("%s, %s!", c.Greeting, name)))
		}
		if err := s.Emit(ctx, runnel.ToMain, out, good); err != nil {
			return err
		}
		if err := s.Emit(ctx, runnel.ToError, runnel.ErrorFields(b.Fields), bad); err != nil {
			return err
		}
	}
}
