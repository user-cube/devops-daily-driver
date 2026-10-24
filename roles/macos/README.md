# macos

| Tasks | Tags | |
|---|---|---|
| `macos.yml` | `macos`, `dock`, `menubar`, `finder`, `keyboard`, `appearance`, `screenshots` | macOS `defaults`: what each one sets is in [the main README](../../README.md#macos-settings) |
| `touchid.yml` | `macos`, `touchid` | Touch ID for sudo in `/etc/pam.d/sudo_local` (survives macOS updates), after `pam_reattach` so it also works inside tmux; skipped over SSH. Needs the sudo password asked at the start of the run |
| `permissions.yml` | `permissions`, `aerospace` (never in a full run) | the privacy permissions guide below |

## permissions

macOS only lets the user grant privacy permissions, so this opens System
Settings → Privacy & Security → Accessibility, reveals the sketchybar binary in
Finder, waits for Enter, then reloads SketchyBar to bring up the Automation
prompts. `daily-driver.yml` runs it as a post task, after every role, so
AeroSpace and SketchyBar are already installed.

```bash
ansible-playbook daily-driver.yml --tags permissions
```

Run it again after `brew upgrade sketchybar`: the grant is tied to the exact
binary under `/opt/homebrew/Cellar/sketchybar/<version>/`, so an upgrade drops
it (the Slack/Discord badges turn grey). The full table is in
[the main README](../../README.md#privacy-permissions-aerospace-setup).
