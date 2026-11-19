package core

import (
	"context"
	"errors"
	"log/slog"
	"time"

	"github.com/runnelhq/runnel/internal/action"
	"github.com/runnelhq/runnel/internal/model"
)

// core.wait waits for a given time; it ends early when the run is cancelled.
var waitDefinition = action.Definition{
	Type:        "core.wait",
	Description: "Waits for a given time",
	New:         newWait,
}

type wait struct {
	Duration string `json:"duration"`
}

func newWait(with map[string]any) (action.Action, error) {
	a := &wait{}
	if err := action.DecodeConfig(with, a); err != nil {
		return nil, err
	}
	if a.Duration == "" {
		return nil, errors.New(`missing required field "duration"`)
	}
	return a, nil
}

func (a *wait) Execute(ctx context.Context, ec *action.ExecContext) (action.Result, error) {
	d, err := model.Duration(a.Duration).Value()
	if err != nil {
		return action.Result{}, err
	}
	ec.Logf(slog.LevelDebug, "waiting %s", d)
	t := time.NewTimer(d)
	defer t.Stop()
	select {
	case <-t.C:
		return action.Result{}, nil
	case <-ctx.Done():
		return action.Result{}, ctx.Err()
	}
}
