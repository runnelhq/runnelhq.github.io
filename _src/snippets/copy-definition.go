// file.copy copies files; it ends early when the run is cancelled.
var copyDefinition = action.Definition{
	Type:        "file.copy",
	Category:    action.CategoryFiles,
	Label:       "Copy Files",
	Description: "Copies files or folders",
	Config:      copyAction{},
	New:         newCopy,
}

type copyAction struct {
	Source    string `json:"source" doc:"File or folder to copy; wildcards allowed" schema:"required,example=C:\\in\\*.csv"`
	Target    string `json:"target" doc:"Target folder" schema:"required,example=D:\\archive"`
	Overwrite bool   `json:"overwrite" doc:"Replace existing files" schema:"default=false"`
}

func newCopy(with map[string]any) (action.Action, error) {
	a := &copyAction{}
	if err := action.DecodeConfig(with, a); err != nil {
		return nil, err // unknown fields, missing required fields, wrong types
	}
	return a, nil
}
