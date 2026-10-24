# terminal

| Tasks | Tags | |
|---|---|---|
| `terminal.yml` | `terminal` | tmux, tmux-fingers (⌘Y), and the tmux plugins |
| `ghostty.yml` | `terminal`, `ghostty` | Ghostty (tip build) |
| `zsh.yml` | `zsh` (`pyenv`, `pipx`, `nvm`) | Oh My Zsh, Powerlevel10k, the zsh plugins, pyenv, pipx, nvm |
| `fonts.yml` | `fonts` | MesloLGS NF (Powerlevel10k), JetBrains Mono Nerd Font (Ghostty), the SketchyBar fonts |
| `nvim.yml` | `nvim` | Neovim |

The configs (Ghostty, tmux, `.zshrc`, `.p10k.zsh`, nvim) come from the dotfiles,
through the `system` role.

## Plugins pinned to a commit

Cloned with `git` at a fixed commit, never Homebrew or a plugin manager, so a run
installs exactly what was tested. Both lists are in `defaults/main.yml`:

| List | Into | Plugins |
|---|---|---|
| `zsh_plugins` | `~/.oh-my-zsh/custom/plugins` (`zsh_plugins_dir`) | zsh-autosuggestions, zsh-syntax-highlighting, fzf-tab |
| `tmux_plugins` | `~/.config/tmux/plugins` (`tmux_plugins_dir`) | tmux-resurrect, tmux-continuum, tmux-fzf-url |

The zsh ones go where Oh My Zsh looks for custom plugins: the dotfiles `.zshrc`
loads them as Oh My Zsh plugins, in its order (fzf-tab before the plugins that
wrap widgets, zsh-syntax-highlighting last). tmux.conf loads the tmux ones with
`run-shell`; there is no TPM.

To update one, change its `version` and run `--tags zsh` or `--tags terminal`.
Renovate (`renovate.json`) opens a PR on the 1st and 15th when master has moved
past a pin, and `plugins-outdated` in the dotfiles shows the same from a shell.
