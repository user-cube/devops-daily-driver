#!/bin/bash
# Lists Homebrew formulae and casks installed on this Mac (by hand, not as a
# dependency) that the playbook never mentions: leftovers to uninstall, or
# tools to add to a role. A name counts as mentioned when it appears as a word
# anywhere in roles/, host_vars/ or daily-driver.yml, so vars and loops count.
# Usage: scripts/brew-drift.sh   (from anywhere; tap warnings are hidden)
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

TEXT=$(find "$REPO/daily-driver.yml" "$REPO/roles" "$REPO/host_vars" \
  \( -name '*.yml' -o -name '*.yaml' \) -exec cat {} +)

drift() { # drift <kind> <names...>
  local kind="$1" name found=0
  shift
  for name in "$@"; do
    # tap/formula names: the playbook may use the short or the full name
    if ! grep -qwF -- "$name" <<<"$TEXT" && ! grep -qwF -- "${name##*/}" <<<"$TEXT"; then
      [ $found = 0 ] && echo "$kind not in the playbook:"
      echo "  $name"
      found=1
    fi
  done
  [ $found = 1 ] || echo "$kind: all in the playbook"
}

# shellcheck disable=SC2046 # one name per word
drift "Formulae" $(brew leaves --installed-on-request 2>/dev/null)
# shellcheck disable=SC2046
drift "Casks" $(brew list --cask -1 2>/dev/null)
