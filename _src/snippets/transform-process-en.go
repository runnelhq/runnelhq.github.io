func (t *upper) Process(ctx context.Context, in <-chan transform.Batch, out *transform.Output) error {
	for b := range in {                 // until all incoming links have ended
		for _, r := range b {
			v, _ := r.Get(t.Field)
			r.Set(t.Field, strings.ToUpper(fmt.Sprint(v)))
			if err := out.Emit(r); err != nil {
				return err              // pipeline cancelled
			}
		}
	}
	return nil
}
