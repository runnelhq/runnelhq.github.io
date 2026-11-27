	Config: transfer{}, // contains only IfExists, no longer Overwrite
	Deprecated: []action.Deprecated{{
		Field: "overwrite", RenamedTo: "ifExists", Use: "ifExists: replace", RemovedIn: "2.0",
		Schema:  &schema.Schema{Type: "boolean", Description: "Replace files that exist in the target"},
		Convert: func(old any) (any, error) { … true → "replace", false → "fail" … },
	}},
