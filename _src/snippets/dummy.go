package core

import (
	"context"
	"errors"

	"github.com/runnelhq/runnel/internal/action"
)

// core.dummy does nothing and always succeeds. It serves as a collection point in the
// design: several branches lead into the dummy (with the join mode of choice, e.g.
// join: all or first), and the following steps hang off the dummy only. When the
// branches change, the following steps keep their links (as known from Apache Hop).
var dummyDefinition = action.Definition{
	Type:        "core.dummy",
	Description: "Does nothing; collects branches into one point",
	New:         newDummy,
}

type dummy struct{}

func newDummy(with map[string]any) (action.Action, error) {
	if len(with) > 0 {
		return nil, errors.New("core.dummy has no configuration")
	}
	return dummy{}, nil
}

func (dummy) Execute(context.Context, *action.ExecContext) (action.Result, error) {
	return action.Result{}, nil
}
