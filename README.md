# Setup MacBook for DevOps Work

An Ansible playbook that sets up a Mac for DevOps work: Homebrew packages and
apps, Kubernetes / IaC / CI tools, cloud CLIs, editors, the terminal, macOS
settings, and the [dotfiles](https://github.com/user-cube/dotfiles).

**The guide is the [wiki](https://github.com/user-cube/devops-daily-driver/wiki)**: installing, running parts, configuration,
the roles, the dotfiles, macOS settings, Raycast, the privacy permissions, the
manual steps, development and troubleshooting.

## Fresh install

Needs the Xcode Command Line Tools (`xcode-select --install`). Then:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install ansible
git clone https://github.com/user-cube/devops-daily-driver.git && cd devops-daily-driver
ansible-galaxy collection install -r requirements.yml
# edit host_vars/localhost.yml: cloud providers, optional tools, your taps
ansible-playbook daily-driver.yml            # --check first for a dry run
```

It asks once for a sudo password (casks with their own installers, Touch ID for
sudo); Enter skips those tasks. Then the by-hand steps:
[Installing](https://github.com/user-cube/devops-daily-driver/wiki/Installing) and [Manual steps](https://github.com/user-cube/devops-daily-driver/wiki/Manual-steps).

## Project structure

```
devops-daily-driver/
├── .github/workflows/       # CI: yamllint, ansible-lint, syntax-check, pytest; --check on macOS
├── renovate.json            # updates: Actions, CI lint tools, pinned plugins
├── .ansible-lint            # Rule config, with deferred rules documented
├── .yamllint                # Line length, ignores .ansible/
├── ansible.cfg              # Inventory path, deprecation_warnings
├── inventory.yml            # Explicit localhost (avoids Ansible warnings)
├── daily-driver.yml         # Main playbook
├── requirements.yml         # Galaxy collections
├── host_vars/
│   └── localhost.yml        # Machine-specific variables (cloud providers, etc.)
├── tests/                   # pytest: README, roles, pins and Renovate agree
├── scripts/
│   └── brew-drift.sh        # Homebrew packages the playbook doesn't know about
└── roles/                   # one README per role with more to it: roles/README.md
    ├── system/              # preflight, directories, dotfiles, local-restore
    ├── macos/               # dock, finder, keyboard, Touch ID, permissions guide
    ├── apps/                # ui-apps, cli-apps, docs, networking, Raycast import
    ├── dev-tools/           # git, gnupg, golang, cicd, kubernetes, iac, node, ios
    ├── virtualization/      # docker, colima, buildx (Homebrew)
    ├── editors/             # vscode, jetbrains, neovim, claude code, rtk
    ├── terminal/            # ghostty, tmux + plugins, zsh + plugins, fonts, nvim
    ├── aws/                 # awscli, eksctl, granted
    ├── azure/               # azure-cli
    ├── gcp/                 # google-cloud-sdk
    └── custom-tools/        # custom taps and tools
```

[`roles/README.md`](roles/README.md) has every role's task files, tags and
variables.

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

# New Mac: restore the per-machine files saved with `local-backup` (dotfiles)
# from Bitwarden; existing files are kept. Another machine's backup:
#   -e local_files_machine=Old-Mac
ansible-playbook daily-driver.yml --tags local-restore

# Homebrew packages installed by hand that the playbook doesn't know about
# (leftovers to uninstall, or tools to add to a role)
scripts/brew-drift.sh
```

Tags come in two layers. **Role and area tags** are the ones you normally reach
for:

`system`, `preflight`, `directories`, `dotfiles`, `macos`, `dock`, `finder`,
`keyboard`, `appearance`, `screenshots`, `touchid`, `apps`, `ui-apps`, `cli-apps`,
`logitech`, `networking`, `documentation-tools`, `dev-tools`, `git-tools`, `gh-cli`,
`glab`, `golang`, `golang-tools`, `cicd`, `kubernetes`, `cluster-visualization`,
`kubernetes-cli-tools`, `iac`, `terraform`, `opentofu`, `secrets`, `ai`, `linters`,
`virtualization`, `colima`, `docker-buildx`, `editors`, `terminal`, `ghostty`, `zsh`,
`pyenv`, `pipx`, `nvm`, `fonts`, `nvim`, `aws`, `azure`, `gcp`, `custom-tools`,
`demo`, `menubar`, `node`, `ios`, `krr`, `krew`.

**Feature tags** cut across roles: `aerospace` runs everything for the window
manager setup (AeroSpace, borders, SketchyBar, its fonts, macOS Spaces/menu bar
tweaks, dotfiles sync) and ends with the interactive `permissions` guide.
`taps` adds only the Homebrew taps and trusts their formulae: CI runs it for
real before the whole playbook in `--check` (a tap isn't added in check mode,
and installing from it would then fail).

**By hand only** (tagged `never`, so a full run skips them): `permissions`,
`raycast-import`, `local-restore`.

Individual packages also carry their own tag (`bat`, `jq`, `htop`, `k9s`, …), so
you can install a single tool without running its whole role:

```bash
ansible-playbook daily-driver.yml --tags k9s
```

## Development

```bash
yamllint .
ansible-lint
ansible-playbook --syntax-check daily-driver.yml
pytest tests/
```

CI runs the same, plus the whole playbook with `--check` on macOS. Details:
[Development](https://github.com/user-cube/devops-daily-driver/wiki/Development).
