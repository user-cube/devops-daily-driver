# dev-tools

| Tasks | Tags | |
|---|---|---|
| `git.yml` | `git-tools`, `gh-cli` | git tools, gnupg + pinentry-mac (writes `~/.gnupg/gpg-agent.conf`), gh, glab |
| `golang.yml` | `golang`, `golang-tools` | Go and Go tools |
| `cicd.yml` | `cicd` | CI/CD tools |
| `kubernetes.yml` | `kubernetes`, `cluster-visualization`, `kubernetes-cli-tools` | Headlamp, Freelens, k9s, stern, kubectl, helm, helm-docs, kyverno, kubeconform, kubecolor, dyff, krr; helmfile and kubelogin when enabled |
| `iac.yml` | `iac` | terraform-docs, terraform-ls, tenv, ansible-lint, tflint, the OpenTofu language server; age, sops, bitwarden-cli; tfsec when enabled |
| `node.yml` | `node` | yarn, corepack, when enabled |
| `ios.yml` | `ios` | xcodegen, ldid, zsign, dpkg (signing iOS apps outside the App Store), when enabled |

Optional, all default `false` (`defaults/main.yml`, override in `host_vars`):

| Variable | Installs |
|---|---|
| `install_kubelogin` | kubelogin, the OIDC login plugin for kubectl |
| `install_helmfile` | helmfile (ArgoCD deploys the charts instead) |
| `install_tfsec` | tfsec (trivy config covers it) |
| `install_node` | yarn, corepack |
| `install_ios` | the iOS signing tools |

Commit signing (GPG, or SSH keys from an agent) is in
[the main README](../../README.md#commit-signing).
