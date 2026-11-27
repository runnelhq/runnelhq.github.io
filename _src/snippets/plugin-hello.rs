use runnel_plugin::{Action, Config, Plugin};
use serde::Deserialize;

#[derive(Deserialize, Config, Default)]
#[serde(default)]
struct GreetConfig {
    /// Whom to greet
    #[runnel(required, example = "World")]
    name: String,
    /// Capital letters
    shout: bool,
}

fn main() {
    let mut p = Plugin::new("hello", "1.0.0"); // name and version as in plugin.yaml
    p.action(Action::new("hello.greet", "Greet", "Returns a greeting for a name", |call, c: GreetConfig| {
        call.log.info(format_args!("greeting {}", c.name));
        Ok(serde_json::json!({ "message": format!("Hello, {}!", c.name) }))
    }));
    p.main();
}
