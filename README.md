# Setup MacBook for DevOps Work

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
    ├── dev-tools/           # git, golang, cicd, kubernetes, iac
    ├── virtualization/      # docker, colima, buildx
    ├── editors/             # vscode, cursor, jetbrains, neovim
    ├── terminal/            # warp, ghostty, zsh, fonts, nvim
    ├── aws/                 # awscli, eksctl, granted
    ├── azure/               # azure-cli
    ├── gcp/                 # google-cloud-sdk
    └── custom-tools/        # imagemagick, gifsicle, user-cube tools
```

## Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Install Ansible

```bash
brew install ansible
```

## Install Ansible Galaxy collections

The playbook uses `community.general` (homebrew, homebrew_cask, homebrew_tap) and `ansible.posix` (synchronize for dotfiles):

```bash
ansible-galaxy collection install -r requirements.yml
```

## Run the playbook

```bash
ansible-playbook daily-driver.yml -K
```

Pre-flight checks (Homebrew installed, macOS only) run automatically on every play.

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

## Cloud providers

Cloud provider roles are **opt-in** and default to `false`. Enable them in `host_vars/localhost.yml`:

```yaml
install_aws: true
install_azure: false
install_gcp: false
```

Or override on the fly:

```bash
ansible-playbook daily-driver.yml -K -e install_aws=true
```

You can also combine with tags to run a single provider:

```bash
ansible-playbook daily-driver.yml -K --tags aws -e install_aws=true
```

After installing AWS tools, verify:

```bash
aws --version && eksctl version && aws-iam-authenticator version && granted --version
```

## Configuration variables

Machine-specific variables live in `host_vars/localhost.yml`. Role-specific defaults (dotfiles repo, font URLs, nvim config, etc.) are in each role's `vars/main.yml`.

To override without editing files:

```bash
# Different dotfiles repository
ansible-playbook daily-driver.yml -K --tags dotfiles -e "dotfiles_repo=https://github.com/your-user/dotfiles.git"
```

## Dotfiles

Clones the repository defined in `roles/system/vars/main.yml`, syncs `.config` and `.config_macos` to `~/.config`, copies `.zshrc_macos` to `~/.zshrc`, and copies any of `.gitconfig`, `.gitconfig-personal`, `.gitconfig-work` if present. Syncing `.config_macos` triggers a restart of Yabai and skhd-zig.

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
