// namespaces lists the Register functions of all built-in namespaces.
// A new namespace is added here and nowhere else.
var namespaces = []func(*action.Registry){
	core.Register,
}

// Builtin returns a new registry with all built-in actions.
func Builtin() *action.Registry {
	r := action.NewRegistry()
	for _, register := range namespaces {
		register(r)
	}
	return r
}
