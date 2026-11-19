func (a *copyAction) Execute(ctx context.Context, ec *action.ExecContext) (action.Result, error) {
	ec.Logf(slog.LevelDebug, "copying %s to %s", a.Source, a.Target)
	…
	if err := ctx.Err(); err != nil {
		return action.Result{}, err
	}
	ec.Logf(slog.LevelInfo, "copied %d files", n)
	return action.Result{}, nil
}
