# Roles

`daily-driver.yml` runs them in this order. Each has `tasks/main.yml`, which
imports one file per area with its own tags, and most have `defaults/main.yml`
(override in `host_vars/localhost.yml`). The roles with more to them have their
own README.

| Role | Task files (tags) | Installs / does | Variables |
|---|---|---|---|
| [`system`](system/README.md) | `preflight` (always), `directories`, `dotfiles`; `local-files` (`local-restore`, never by default) | Homebrew and macOS checks, `~` folders, the dotfiles | `dotfiles_repo`, `dotfiles_dest`, `directories_to_create` |
| [`macos`](macos/README.md) | `macos` (`dock`, `menubar`, `finder`, `keyboard`, `appearance`, `screenshots`), `touchid`; `permissions` (never by default) | macOS `defaults`, Touch ID for sudo, the privacy permissions guide | |
| [`apps`](apps/README.md) | `ui-apps`, `cli-apps`, `documentation-tools`, `networking` | casks, CLI tools, AeroSpace + borders + SketchyBar (started if not running), Raycast import | `felixkratz_tools`, `raycast_bitwarden_attachment` |
| `aws` | `aws` | awscli, aws-iam-authenticator, eksctl, granted | `install_aws` (default false) |
| `azure` | `azure` | azure-cli | `install_azure` (default false) |
| `gcp` | `gcp` | google-cloud-sdk | `install_gcp` (default false) |
| [`dev-tools`](dev-tools/README.md) | `git-tools` / `gh-cli`, `golang`, `cicd`, `kubernetes`, `iac`, `node`, `ios` | git, GPG, gh, glab, Go, CI/CD, Kubernetes, Terraform/OpenTofu, secrets tools | `krew_plugins`; `install_kubelogin`, `install_node`, `install_ios`, `install_tfsec`, `install_helmfile` (default false) |
| `virtualization` | `virtualization` | Docker CLI, Colima (a stopped `work` profile), Buildx, hadolint, lazydocker | |
| `editors` | `editors` | VS Code, JetBrains, Neovim, Claude Code, rtk | |
| [`terminal`](terminal/README.md) | `terminal`, `ghostty`, `zsh`, `fonts`, `nvim` | tmux and its plugins, Ghostty, Oh My Zsh + Powerlevel10k + zsh plugins, pyenv, pipx, nvm, fonts | `zsh_plugins`, `tmux_plugins`, fonts |
| `custom-tools` | `custom-tools`, `demo` | your own taps, formulae and casks | `custom_user_taps`, `custom_user_tools`, `custom_user_casks` |

Every task also carries `install`, and packages carry their own tag (`k9s`,
`jq`, …): `ansible-playbook daily-driver.yml --tags k9s` installs one tool.
The cloud roles skip everything unless their `install_*` is true.
