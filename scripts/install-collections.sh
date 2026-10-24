#!/bin/bash
# The Galaxy collections of requirements.yml: from Galaxy, and when Galaxy fails
# (it answers 500 now and then, sometimes for hours) the same versions from
# their GitHub repos, ansible-collections/<name> at the tag <version>. Used by CI;
# extra arguments go to ansible-galaxy (e.g. -p DIR).
set -euo pipefail
cd "$(dirname "$0")/.."

ansible-galaxy collection install -r requirements.yml "$@" && exit 0

echo "Galaxy failed: installing the same versions from GitHub" >&2
# "name version" of each collection (requirements.yml: - name: x / version: "y")
pins=$(awk '/- name:/ {n = $3} /version:/ {gsub(/"/, "", $2); print n, $2}' requirements.yml)
[ -n "$pins" ] || { echo "install-collections.sh: no collection in requirements.yml" >&2; exit 1; }
while read -r name version; do
  ansible-galaxy collection install "git+https://github.com/ansible-collections/$name.git,$version" "$@"
done <<<"$pins"
