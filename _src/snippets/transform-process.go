func (t *upper) Process(ctx context.Context, in <-chan transform.Batch, out *transform.Output) error {
	for b := range in {                 // bis alle eingehenden Links beendet sind
		for _, r := range b {
			v, _ := r.Get(t.Field)
			r.Set(t.Field, strings.ToUpper(fmt.Sprint(v)))
			if err := out.Emit(r); err != nil {
				return err              // Pipeline abgebrochen
			}
		}
	}
	return nil
}
