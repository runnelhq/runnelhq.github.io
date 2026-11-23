// file.copy copies files; it ends early when the run is cancelled.
var copyDefinition = action.Definition{
	Type:        "file.copy",
	Description: "Copies files or folders",
	New:         newCopy,
}

type copyAction struct {
	Source    string `json:"source"`
	Target    string `json:"target"`
	Overwrite bool   `json:"overwrite"`
}

func newCopy(with map[string]any) (action.Action, error) {
	a := &copyAction{}
	if err := action.DecodeConfig(with, a); err != nil {
		return nil, err // unknown fields, wrong types
	}
	if a.Source == "" {
		return nil, errors.New(`missing required field "source"`)
	}
	return a, nil
}
