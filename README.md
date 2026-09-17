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
    ├── virtualization/      # docker, colima, buildx
    ├── editors/             # vscode, cursor, jetbrains, neovim
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
```

Tags come in two layers. **Role and area tags** are the ones you normally reach
for:

`system`, `preflight`, `directories`, `dotfiles`, `macos`, `dock`, `finder`,
`keyboard`, `apps`, `ui-apps`, `cli-apps`, `logitech`, `networking`,
`documentation-tools`, `dev-tools`, `git-tools`, `gh-cli`, `glab`, `golang`,
`cicd`, `kubernetes`, `cluster-visualization`, `iac`, `terraform`, `opentofu`,
`secrets`, `linters`, `virtualization`, `colima`, `docker-buildx`, `editors`,
`terminal`, `ghostty`, `zsh`, `pyenv`, `nvm`, `fonts`, `nvim`, `aws`, `azure`,
`gcp`, `custom-tools`, `demo`.

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

Clones the repository defined in `host_vars/localhost.yml`, syncs `.config` and `.config_macos` to `~/.config`, copies `.zshrc_macos` to `~/.zshrc`, and copies any of `.gitconfig`, `.gitconfig-personal`, `.gitconfig-work` if present. Syncing `.config_macos` triggers a restart of Yabai and skhd-zig.

## macOS settings

The `macos` role configures:
- **Dock** — size, position (right), magnification, animation, indicators
- **Finder** — extensions, hidden files, path bar, status bar, column view
- **Keyboard** — full keyboard access, Spotlight shortcuts disabled, Siri disabled

  Both Spotlight and Siri bind ⌘Space; Siri's default is *hold* ⌘Space, which
  swallows the keystroke before any app sees it. The playbook frees the shortcut
  but **cannot set Raycast's hotkey** — Raycast keeps it in an encrypted internal
  database with no supported `defaults` key. See [Manual steps](#manual-steps).

## Services (Yabai, skhd-zig)

The `cli-apps` tasks check with `pgrep` whether each service is running and start
it if not, so "running" is the desired state rather than a side effect of the
install task firing a handler. Syncing dotfiles `.config_macos` still triggers a
restart of both services through handlers.

## Ghostty

Installs Ghostty (tip/development build) and syncs config from dotfiles if `dotfiles/.config/ghostty/` exists.

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

## Manual steps

The playbook cannot automate these:

| Step | Why |
|------|-----|
| Raycast hotkey (Settings → General) | stored in an encrypted internal database |
| Register the signing key on GitHub | account-side, needs your session |
| Fill in `~/.gitconfig-work` | the repo ships a redacted placeholder; `force: false` keeps your local value |
| Approve system extensions | Logitech and similar installers need Privacy & Security approval |

## Development

Lint and validate before pushing — CI runs the same three checks:

```bash
yamllint .
ansible-lint
ansible-playbook --syntax-check daily-driver.yml
```

`.ansible-lint` carries a `skip_list` of rules that are deliberately deferred
rather than disabled; each entry is commented with what it covers.
