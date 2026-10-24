# system

| Tasks | Tags | |
|---|---|---|
| `preflight.yml` | `always`, `preflight` | fails early without Homebrew or off macOS |
| `directories.yml` | `directories` | creates `directories_to_create` in `~` (default `personal`, `work`, `hooks`) |
| `dotfiles.yml` | `dotfiles` | installs the dotfiles, below |
| `local-files.yml` | `local-restore` (never by default) | restores the per-machine files from Bitwarden |

## dotfiles

Clones `dotfiles_repo` to `dotfiles_dest` (`~/dotfiles`), then does what
`dotfiles-sync` does in the dotfiles repo:

- syncs `.config/` to `~/.config/`, `git_hooks/` to `~/git_hooks/` and
  `claude/` to `~/.claude/` (rsync: never deletes; the dotfiles' `obsolete`
  list does that)
- adds `Include ~/.config/ssh/*.conf` at the top of `~/.ssh/config` (ControlMaster
  defaults; the rest of that file stays per machine)
- copies `.zshrc` and `.p10k.zsh` (overwritten every run: per-machine shell
  config goes in `~/.zshrc.local`), and the gitconfigs; `.gitconfig-work` only
  when missing (the repo holds a placeholder)
- installs Go and runs the dotfiles' `.config/dotfiles/install.sh`: builds the
  Go tools, downloads the SketchyBar icon map, installs the Hue VS Code
  extension, removes obsolete files. A new step goes in that script, not here
- reloads tmux, AeroSpace, borders and SketchyBar through handlers when
  something changed

## local-restore

`local-backup` (dotfiles) keeps the files that never go to git in a Bitwarden
note per machine; on a new Mac:

```bash
ansible-playbook daily-driver.yml --tags local-restore                          # this machine's backup
ansible-playbook daily-driver.yml --tags local-restore -e local_files_machine=Old-Mac
```

Existing files are kept. It needs a Bitwarden session: the one the dotfiles
`bw` wrapper saved, or an exported `BW_SESSION`.
