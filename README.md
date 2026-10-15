# Setup MacBook for DevOps Work

## Prerequisites

- macOS (Apple Silicon or Intel)
- Xcode Command Line Tools:

```bash
xcode-select --install
```

## Fresh install

Follow these steps in order on a new machine:

```bash
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Ansible
brew install ansible

# 3. Clone this repo
git clone https://github.com/your-user/devops-daily-driver.git
cd devops-daily-driver

# 4. Install Ansible Galaxy collections
ansible-galaxy collection install -r requirements.yml

# 5. Configure your machine variables
cp host_vars/localhost.yml host_vars/localhost.yml.bak
# Edit host_vars/localhost.yml with your settings

# 6. Run the playbook
ansible-playbook daily-driver.yml
```

The playbook prompts once for a sudo password. It is only used by casks that ship
their own installers (currently the Logitech ones) — press enter to skip it and
those tasks will fail while everything else proceeds. No task uses `become`, so
`-K` is not needed.

Preview a run without changing anything:

```bash
ansible-playbook daily-driver.yml --check
```

## Project structure

```
devops-daily-driver/
├── .github/workflows/       # CI: yamllint, ansible-lint, syntax-check
├── .ansible-lint            # Rule config, with deferred rules documented
├── .yamllint                # Line length, ignores .ansible/
├── ansible.cfg              # Inventory path, deprecation_warnings
├── inventory.yml            # Explicit localhost (avoids Ansible warnings)
├── daily-driver.yml         # Main playbook
├── requirements.yml         # Galaxy collections
├── host_vars/
│   └── localhost.yml        # Machine-specific variables (cloud providers, etc.)
└── roles/
    ├── system/              # preflight, directories, dotfiles
    ├── macos/               # dock, finder, keyboard shortcuts
    ├── apps/                # ui-apps, cli-apps, docs, networking
    ├── dev-tools/           # git, gnupg, golang, cicd, kubernetes, iac
    ├── virtualization/      # docker, colima, buildx (Homebrew)
    ├── editors/             # vscode, jetbrains, neovim
    ├── terminal/            # ghostty, zsh, tmux, fonts, nvim
    ├── aws/                 # awscli, eksctl, granted
    ├── azure/               # azure-cli
    ├── gcp/                 # google-cloud-sdk
    └── custom-tools/        # custom taps and tools
```

## Run only specific roles (tags)

```bash
# Only macOS settings
ansible-playbook daily-driver.yml --tags macos

# Only CLI apps
ansible-playbook daily-driver.yml --tags cli-apps

# Only dotfiles
ansible-playbook daily-driver.yml --tags dotfiles

# Only the AeroSpace setup (WM, borders, SketchyBar, fonts, macOS tweaks, dotfiles,
# then the interactive permissions guide)
ansible-playbook daily-driver.yml --tags aerospace

# Only the permissions guide (e.g. after `brew upgrade sketchybar`)
ansible-playbook daily-driver.yml --tags permissions
```

Tags come in two layers. **Role and area tags** are the ones you normally reach
for:

`system`, `preflight`, `directories`, `dotfiles`, `macos`, `dock`, `finder`,
`keyboard`, `apps`, `ui-apps`, `cli-apps`, `logitech`, `networking`,
`documentation-tools`, `dev-tools`, `git-tools`, `gh-cli`, `glab`, `golang`,
`cicd`, `kubernetes`, `cluster-visualization`, `iac`, `terraform`, `opentofu`,
`secrets`, `linters`, `virtualization`, `colima`, `docker-buildx`, `editors`,
`terminal`, `ghostty`, `zsh`, `pyenv`, `nvm`, `fonts`, `nvim`, `aws`, `azure`,
`gcp`, `custom-tools`, `demo`, `menubar`.

**Feature tags** cut across roles: `aerospace` runs everything for the window
manager setup (AeroSpace, borders, SketchyBar, its fonts, macOS Spaces/menu bar
tweaks, dotfiles sync) and ends with the interactive `permissions` guide.

Individual packages also carry their own tag (`bat`, `jq`, `htop`, `k9s`, …), so
you can install a single tool without running its whole role:

```bash
ansible-playbook daily-driver.yml --tags k9s
```

## Configuration variables

Machine-specific variables live in `host_vars/localhost.yml`. Role-specific defaults are in each role's `defaults/main.yml` and can be overridden via `host_vars`.

Key variables to configure in `host_vars/localhost.yml`:

```yaml
# Cloud providers (opt-in, default false)
install_aws: true
install_azure: false
install_gcp: false

# Dotfiles
dotfiles_repo: "https://github.com/your-user/dotfiles.git"

# Directories to create in $HOME
directories_to_create:
  - personal
  - work

# Custom tools (tap + formulae)
custom_user_taps:
  - your-tap/tap
custom_user_tools:
  - your-tap/tap/tool-name
```

## Cloud providers

Cloud provider roles are **opt-in** and default to `false`. Enable them in `host_vars/localhost.yml` or override on the fly:

```bash
ansible-playbook daily-driver.yml -e install_aws=true
```

Combine with tags to run a single provider:

```bash
ansible-playbook daily-driver.yml --tags aws -e install_aws=true
```

## Dotfiles

Clones the repository defined in `host_vars/localhost.yml` (macOS only), syncs `.config` to
`~/.config`, copies `.zshrc` and `.p10k.zsh` to `~`, and copies any of `.gitconfig`,
`.gitconfig-personal`, `.gitconfig-work` if present. Syncing `.config` reloads tmux,
AeroSpace, borders and SketchyBar.
lazygit's macOS config path (`~/Library/Application Support/lazygit/config.yml`) is linked to
the synced `~/.config/lazygit/config.yml` (delta diffs, side by side when wide).

`~/.zshrc` is **overwritten** on every run. Anything specific to one machine (work-only
tools, aliases) belongs in `~/.zshrc.local`, which `.zshrc` sources last and the
playbook never touches. Shared shell functions live in dotfiles `.config/zsh/*.zsh` and
are sourced automatically (e.g. `bw.zsh`, the Bitwarden CLI wrapper, which needs
`export BW_USER=<email>` in `~/.zshrc.local`). Tokens and API keys are not stored in
any file: they are fetched from Bitwarden when the tool that needs them starts (see the
Secrets section of the dotfiles README).

Shell startup stays around 0.2 s: nvm loads on first use, `pyenv init` skips the rehash
and tool completions are cached in `~/.cache/zsh` (regenerated when the tool is upgraded).

Other per-machine files, also never overwritten:

| File | Purpose |
|---|---|
| `~/.zshrc.local` | machine-specific shell config (no tokens; see above) |
| `~/.config/tmux/sessions.local` | repos preloaded as tmux sessions |
| `~/.config/sketchybar/aws_profiles` | AWS profiles shown in SketchyBar |

To update a machine without running Ansible, run `dotfiles-sync` (a shell function
from dotfiles `.config/zsh/dotfiles.zsh`): it pulls `~/dotfiles`, syncs the same files
as the `dotfiles` tag and reloads tmux, AeroSpace, SketchyBar and borders.

## macOS settings

The `macos` role configures:
- **Dock** — size, position (right), magnification, animation, indicators
- **Finder** — extensions, hidden files, path bar, status bar, column view
- **Menu bar** — Sound always shown
- **Spaces** — no automatic rearranging of Spaces
- **Keyboard** — full keyboard access, Spotlight shortcuts disabled, Siri disabled; with AeroSpace, Mission Control ctrl ←/→ disabled
- **Touch ID for sudo** — `pam_tid.so` in `/etc/pam.d/sudo_local` (survives macOS updates). Needs the sudo password asked at the start of the run; skipped when left empty. Run alone with `--tags touchid`.

  Both Spotlight and Siri bind ⌘Space; Siri's default is *hold* ⌘Space, which
  swallows the keystroke before any app sees it. The playbook frees the shortcut
  but **cannot set Raycast's hotkey** — Raycast keeps it in an encrypted internal
  database with no supported `defaults` key. See [Manual steps](#manual-steps).

## Window manager (AeroSpace)

Installs [AeroSpace](https://github.com/nikitabobko/AeroSpace) (`nikitabobko/tap/aerospace`).
Config and cheat sheet live in dotfiles `.config/aerospace/`. The `cli-apps`
tasks check with `pgrep` whether it is running and start it if not, so "running"
is the desired state rather than a side effect of the install task. Syncing
dotfiles `.config` reloads it through handlers.

[JankyBorders](https://github.com/FelixKratz/JankyBorders) (`FelixKratz/formulae/borders`)
highlights the focused window; its config lives in dotfiles `.config/borders/bordersrc`.

[SketchyBar](https://github.com/FelixKratz/SketchyBar) (`FelixKratz/formulae/sketchybar`) is a
bottom status bar: AeroSpace workspaces with app icons, focused app, Spotify, Slack, kube
context (red for prod), Colima profiles, GitHub/GitLab reviews, AWS/GCP sessions,
Slack/Discord badges, CPU, RAM, weather and outdated Homebrew packages. Config lives in dotfiles `.config/sketchybar/`;
fonts (`font-sketchybar-app-font`, `font-sf-pro`, `font-hack-nerd-font`) are installed by the `fonts` and `aerospace` tags.
The GitLab, AWS and GCP items stay hidden until their CLI is logged in.

## Ghostty

Installs Ghostty (tip/development build); its config comes from the dotfiles `.config` sync.


Every Ghostty window starts inside **tmux** (`.config/ghostty/tmux-start.sh` in
dotfiles): Ghostty's native tabs are separate macOS windows that AeroSpace tiles,
so tabs, splits and sessions come from tmux instead, driven by the usual ⌘
shortcuts (⌘T, ⌘⇧←/→, ⌘1–9, ⌘D, ⌘W, ⌘⇧S for sessions). The first window attaches
the persistent `main` session; extra windows get throwaway sessions. ⌘O opens any repo
under `~/work` as a session, ⌘G opens lazygit in a popup. Sessions survive reboots
via tmux-resurrect + tmux-continuum, cloned by the playbook at pinned commits
(`tmux_plugins` in `roles/terminal/defaults/main.yml`) into `~/.config/tmux/plugins`. Config:
dotfiles `.config/tmux/tmux.conf`. tmux is installed by the `terminal` and
`aerospace` tags.

## Neovim

Installs `neovim` via Homebrew. Config is managed via dotfiles.

## Commit signing

The `dev-tools` role installs `gnupg` and `pinentry-mac` and writes
`~/.gnupg/gpg-agent.conf`, so GPG signing works if you already carry a key.

If you keep your SSH keys in an agent (1Password, Bitwarden, `ssh-agent`), SSH
signing is less work than maintaining a GPG keyring — git has supported it since
2.34 and there is no key material on disk:

```ini
# ~/.gitconfig-personal
[user]
    email = <id>+<user>@users.noreply.github.com
    signingkey = key::ssh-ed25519 AAAA...
[gpg]
    format = ssh
[commit]
    gpgsign = true
```

The `key::` prefix means "this is the key itself", not a path — git hands the
public key to the agent, which signs with the private half. Register the *same*
public key on GitHub a second time under Settings → SSH and GPG keys, with key
type **Signing Key**; a key registered only for authentication will not verify
signatures.

`git log --show-signature` reports `No signature` until you also point
`gpg.ssh.allowedSignersFile` at a file mapping emails to keys. That is a local
verification concern only — GitHub verifies against the keys on your account.

## Raycast

Raycast keeps its settings in a SQLCipher-encrypted database and exposes no
deeplink, CLI or `defaults` key to configure it, so nothing about it can be set
declaratively. Two things follow.

The **hotkey stays manual** — set ⌘Space in Settings → General → Raycast Hotkey.
The playbook frees the shortcut by disabling the Spotlight and Siri bindings, but
cannot assign it.

Everything else can travel in a `.rayconfig` export (Settings → Advanced → Export
Settings & Data), which covers extensions and their preferences, quicklinks,
snippets, window layouts and general settings. Point `raycast_config_path` at it
and run:

```bash
ansible-playbook daily-driver.yml --tags raycast-import
```

The task carries the `never` tag, so ordinary runs skip it — otherwise every run
would pop Raycast's import dialog. Import still asks for confirmation; this makes
it one click instead of reconfiguring extension by extension.

> **Keep the export out of a public repo.** It is an opaque blob that may carry
> extension credentials, so secret scanners like gitleaks will not catch them.
> Store it in a password manager or private location. Raycast Pro's Cloud Sync
> (`requiresPro`) removes the need for the file entirely.

## Privacy permissions (AeroSpace setup)

macOS only lets the user grant these. `--tags permissions` (also part of
`--tags aerospace`, never part of a full run) opens the right pane, reveals the
sketchybar binary in Finder and waits for Enter.

| Where (System Settings → Privacy & Security) | App | Why |
|---|---|---|
| Accessibility | AeroSpace (`/Applications/AeroSpace.app`) | move and tile windows |
| Accessibility | sketchybar (`/opt/homebrew/Cellar/sketchybar/<version>/bin/sketchybar`) | read Slack/Discord Dock badges |
| Automation → System Events | sketchybar (prompted on first use) | Dock badges |
| Automation → Spotify | sketchybar (prompted on first use) | play/pause |

**After `brew upgrade sketchybar`** the Cellar path changes and the Accessibility
grant is lost (badges turn grey): remove the old entry and run `--tags permissions`.

## Manual steps

The playbook cannot automate these:

| Step | Why |
|------|-----|
| Raycast hotkey (Settings → General) | stored in an encrypted internal database |
| Register the signing key on GitHub | account-side, needs your session |
| Fill in `~/.gitconfig-work` | the repo ships a redacted placeholder; `force: false` keeps your local value |
| Approve system extensions | Logitech and similar installers need Privacy & Security approval |
| AeroSpace Accessibility permission | TCC prompt, needs user approval |
| Keep a single macOS Desktop | AeroSpace only manages windows on the current Space |
| Firefox `full-screen-api.macos-native-full-screen = false` | `about:config`, per profile; avoids fullscreen video creating its own Space |

## Development

Lint and validate before pushing — CI runs the same three checks:

```bash
yamllint .
ansible-lint
ansible-playbook --syntax-check daily-driver.yml
```

`.ansible-lint` carries a `skip_list` of rules that are deliberately deferred
rather than disabled; each entry is commented with what it covers.
