// Package core contains the basic workflow actions of the namespace "core":
// core.start, core.success, core.abort, core.log, core.wait and core.dummy.
//
// Each action lives in a file of its own (<name>.go) with its tests next to it
// (<name>_test.go); Register lists all actions of the namespace (ADR 0013).
package core

import "github.com/runnelhq/runnel/internal/action"

// Register adds all actions of the namespace "core" to a registry.
func Register(r *action.Registry) {
	r.Register(startDefinition)
	r.Register(successDefinition)
	r.Register(abortDefinition)
	r.Register(logDefinition)
	r.Register(waitDefinition)
	r.Register(dummyDefinition)
}
