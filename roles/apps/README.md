# apps

| Tasks | Tags | |
|---|---|---|
| `ui-apps.yml` | `ui-apps` | Homebrew casks, the Logitech tools (their installers need the sudo password), the Raycast import (`raycast-import`, never by default) |
| `cli-apps.yml` | `cli-apps` | CLI tools, linters, monitoring; AeroSpace, glow, lazygit; borders and SketchyBar (FelixKratz tap, `felixkratz_tools`) as Homebrew services |
| `docs.yml` | `documentation-tools` | documentation tools |
| `networking.yml` | `networking` | networking tools |

AeroSpace, borders and SketchyBar are checked with `pgrep` and started when they
are not running: "running" is the state the run leaves, not a side effect of
installing them. Their configs come from the dotfiles (`system` role).

## Raycast import

Raycast keeps its settings in an encrypted database, so the playbook can only
open the import of a `.rayconfig` export, from an attachment
(`raycast_bitwarden_attachment`, default `raycast.rayconfig`) of the Bitwarden
item `raycast_bitwarden_item`, or a local `raycast_config_path`. It needs a
Bitwarden session and Raycast installed, so it runs by hand after the first run:

```bash
ansible-playbook daily-driver.yml --tags raycast-import   # give the sudo password
```

More in [the main README](../../README.md#raycast).
