package core

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/runnelhq/runnel/internal/record"
	"github.com/runnelhq/runnel/internal/transform"
)

// core.filter passes on the records for which a condition is true.
var filterDefinition = transform.Definition{
	Parallel:     true,
	Type:         "core.filter",
	RecordErrors: true,
	Category:     transform.CategoryTransform,
	Label:        "Filter",
	Description:  "Passes on the records for which a condition is true",
	Example:      "condition: \"{{ record.umsatz > 0 && record.ort != '' }}\"\n",
	Config:       filter{},
	New:          newFilter,
}

type filter struct {
	Condition string `json:"condition" doc:"Expression that must be true for a record to pass, e.g. {{ record.amount > 0 }}; a comparison with an empty value is false" schema:"required,example={{ record.amount > 0 }}"`

	cond *transform.Expression
}

func newFilter(with map[string]any) (transform.Transform, error) {
	t := &filter{}
	if err := transform.DecodeConfig(with, t); err != nil {
		return nil, err
	}
	cond, err := transform.CompileExpression(t.Condition)
	if err != nil {
		return nil, fmt.Errorf("condition: %w", err)
	}
	t.cond = cond
	return t, nil
}

// Init checks the fields of the condition and passes the schema on: the records stay as
// they are.
func (t *filter) Init(ic *transform.InitContext) (record.Schema, error) {
	for _, f := range t.cond.Fields() {
		ic.Use(f, "condition")
	}
	return ic.In, nil
}

func (t *filter) Process(ctx context.Context, in <-chan transform.Batch, out *transform.Output) error {
	var read, kept, failed int64
	for b := range in {
		for _, r := range b {
			read++
			ok, err := t.cond.Bool(out, r)
			if err != nil {
				// To an error link, or the pipeline stops.
				failed++
				if err := out.Fail(r, "", fmt.Errorf("record %d: %w", read, err)); err != nil {
					return err
				}
				continue
			}
			if !ok {
				continue
			}
			kept++
			if err := out.Emit(r); err != nil {
				return err
			}
		}
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	if failed > 0 {
		out.Logf(slog.LevelInfo, "kept %d of %d records, dropped %d, %d with errors", kept, read, read-kept-failed, failed)
	} else {
		out.Logf(slog.LevelInfo, "kept %d of %d records, dropped %d", kept, read, read-kept)
	}
	return nil
}
