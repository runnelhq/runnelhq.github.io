package core

import (
	"context"
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/runnelhq/runnel/internal/actions/actiontest"
)

func TestWaitConfig(t *testing.T) {
	actiontest.ConfigError(t, waitDefinition, nil, `missing required field "duration"`)
}

func TestWait(t *testing.T) {
	a := actiontest.New(t, waitDefinition, map[string]any{"duration": "20ms"})
	start := time.Now()
	if _, _, err := actiontest.Execute(context.Background(), a); err != nil || time.Since(start) < 20*time.Millisecond {
		t.Errorf("returned after %v, err %v", time.Since(start), err)
	}

	a = actiontest.New(t, waitDefinition, map[string]any{"duration": ""})
	if _, _, err := actiontest.Execute(context.Background(), a); err == nil || err.Error() != "no duration given" {
		t.Errorf("empty duration: %v", err)
	}

	a = actiontest.New(t, waitDefinition, map[string]any{"duration": "soon"})
	if _, _, err := actiontest.Execute(context.Background(), a); err == nil || !strings.Contains(err.Error(), "invalid duration") {
		t.Errorf("invalid duration: %v", err)
	}
}

func TestWaitCancelled(t *testing.T) {
	a := actiontest.New(t, waitDefinition, map[string]any{"duration": "1h"})
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, _, err := actiontest.Execute(ctx, a); !errors.Is(err, context.Canceled) {
		t.Errorf("cancelled wait: %v", err)
	}
}
