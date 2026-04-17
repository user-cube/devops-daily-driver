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
ansible-playbook daily-driver.yml -K
```

## Project structure

```
devops-daily-driver/
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
ansible-playbook daily-driver.yml -K --tags macos

# Only CLI apps
ansible-playbook daily-driver.yml -K --tags cli-apps

# Only dotfiles
ansible-playbook daily-driver.yml -K --tags dotfiles
```

Available tags: `system`, `preflight`, `directories`, `dotfiles`, `macos`, `dock`, `finder`, `keyboard`, `apps`, `ui-apps`, `cli-apps`, `networking`, `dev-tools`, `git-tools`, `golang`, `cicd`, `kubernetes`, `iac`, `virtualization`, `editors`, `terminal`, `ghostty`, `zsh`, `fonts`, `nvim`, `aws`, `azure`, `gcp`, `custom-tools`.

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
ansible-playbook daily-driver.yml -K -e install_aws=true
```

Combine with tags to run a single provider:

```bash
ansible-playbook daily-driver.yml -K --tags aws -e install_aws=true
```

## Dotfiles

Clones the repository defined in `host_vars/localhost.yml`, syncs `.config` and `.config_macos` to `~/.config`, copies `.zshrc_macos` to `~/.zshrc`, and copies any of `.gitconfig`, `.gitconfig-personal`, `.gitconfig-work` if present. Syncing `.config_macos` triggers a restart of Yabai and skhd-zig.

## macOS settings

The `macos` role configures:
- **Dock** — size, position (right), magnification, animation, indicators
- **Finder** — extensions, hidden files, path bar, status bar, column view
- **Keyboard** — full keyboard access, Spotlight disabled, Raycast bound to ⌘Space

## Services (Yabai, skhd-zig)

Yabai and skhd-zig are started via handlers after install. Start handlers are idempotent — they only start a service if it is not already running (`pgrep`). Syncing dotfiles `.config_macos` triggers a restart of both services.

## Ghostty

Installs Ghostty (tip/development build) and syncs config from dotfiles if `dotfiles/.config/ghostty/` exists.

## Neovim

Installs `neovim` via Homebrew. Config is managed via dotfiles.

## GPG

The `dev-tools` role installs `gnupg` and `pinentry-mac`, and configures `~/.gnupg/gpg-agent.conf` automatically.

To generate a key and add it to GitHub:

```bash
# Generate key (RSA 4096, no expiry)
gpg --full-generate-key

# Get the key ID
gpg --list-secret-keys --keyid-format=long

# Export public key and add to GitHub → Settings → SSH and GPG keys
gpg --armor --export <KEY_ID>

# Configure git to sign commits
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
echo 'export GPG_TTY=$(tty)' >> ~/.zshrc
```
