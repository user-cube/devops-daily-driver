"""What the playbook, its README and Renovate's config must agree on: the tags
you can run, the roles, the plugins pinned to a commit, the pinned versions."""

import json
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
ROLES = sorted(p.name for p in (REPO / "roles").iterdir() if (p / "tasks").is_dir())
README = (REPO / "README.md").read_text()
TERMINAL_DEFAULTS = yaml.safe_load((REPO / "roles/terminal/defaults/main.yml").read_text())
PINNED = TERMINAL_DEFAULTS["zsh_plugins"] + TERMINAL_DEFAULTS["tmux_plugins"]
# Tags on every task, for Ansible itself, not for running a part of the playbook
NOT_FOR_RUNNING = {"install", "always", "never"}


def readme_tags() -> set:
    """The tags the README lists, from "Tags come in two layers" up to the
    individual packages' ones."""
    section = README.split("Tags come in two layers", 1)[1].split("Individual packages", 1)[0]
    return set(re.findall(r"`([a-z0-9-]+)`", section))


def runnable_tags() -> set:
    """The tags of the roles, of each task file they import, and of the post
    tasks: the ones that pick a part of the playbook (not each package's own)."""
    tags = set()
    playbook = yaml.safe_load((REPO / "daily-driver.yml").read_text())[0]
    for entry in playbook["roles"] + playbook.get("post_tasks", []):
        tags.update(entry.get("tags", []))
    for role in ROLES:
        for item in yaml.safe_load((REPO / "roles" / role / "tasks/main.yml").read_text()) or []:
            if "import_tasks" in item or "include_tasks" in item:
                tags.update(item.get("tags", []))
    return tags - NOT_FOR_RUNNING


def test_every_runnable_tag_is_in_the_readme():
    missing = runnable_tags() - readme_tags()
    assert not missing, f"tags the README doesn't list: {sorted(missing)}"


@pytest.mark.parametrize("role", ROLES)
def test_role_is_in_the_roles_readme(role):
    table = (REPO / "roles/README.md").read_text()
    assert re.search(rf"\| \[?`{re.escape(role)}`", table), f"{role} has no row in roles/README.md"
    if (REPO / "roles" / role / "README.md").exists():
        assert f"({role}/README.md)" in table, f"roles/README.md doesn't link {role}/README.md"


@pytest.mark.parametrize("plugin", PINNED, ids=lambda p: p["name"])
def test_plugin_is_pinned_to_a_commit(plugin):
    assert plugin["repo"].startswith("https://github.com/")
    assert re.fullmatch(r"[0-9a-f]{40}", str(plugin["version"])), "version must be a full commit"


def test_renovate_finds_every_pinned_plugin():
    """If the defaults' layout changes, Renovate's regex silently stops matching
    and the pins stop moving."""
    config = json.loads((REPO / "renovate.json").read_text())
    manager = next(m for m in config["customManagers"] if m["customType"] == "regex")
    assert "custom.regex" in config["enabledManagers"]
    pattern = re.sub(r"\(\?<(\w+)>", r"(?P<\1>", manager["matchStrings"][0])  # JS to Python groups
    defaults = (REPO / "roles/terminal/defaults/main.yml").read_text()
    found = {(m["depName"], m["currentDigest"]) for m in re.finditer(pattern, defaults)}
    assert found == {(p["repo"], p["version"]) for p in PINNED}


def test_galaxy_collections_are_pinned():
    for collection in yaml.safe_load((REPO / "requirements.yml").read_text())["collections"]:
        assert re.fullmatch(r"\d+\.\d+\.\d+", str(collection.get("version", ""))), collection


def test_ci_tools_are_pinned():
    for line in (REPO / "requirements-ci.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            assert re.fullmatch(r"[A-Za-z0-9_.-]+==[\w.]+", line.strip()), line
