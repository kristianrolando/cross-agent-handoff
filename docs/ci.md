# Automated checks

The GitHub Actions workflow at `.github/workflows/ci.yml` runs on pushes, pull requests and manual dispatch. It uses read-only repository permissions, does not persist checkout credentials, and cancels superseded runs on the same ref. Each job has a ten-minute timeout.

## Matrix

| Runner | Python | Purpose |
| --- | --- | --- |
| ubuntu-latest | 3.9 | Minimum helper language version |
| ubuntu-latest | 3.13 | Newer Python on Linux |
| macos-latest | 3.13 | macOS filesystem behavior |
| windows-latest | 3.13 | Windows paths and line endings |

All four jobs passed in the [first hosted run](https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41401002913) on commit `74d2c5c4c7fae8adf72e3053e4db4cb22f829af2`. This establishes the automated suite on those runners, not model compliance or native host discovery. The badge and Actions history show subsequent results. Local authoring evidence is recorded separately in docs/validation.md.

## Scope

The suite checks checkpoint mechanics, failure injection, dirty Git inventory, portability constraints, metadata, local Markdown file links, example checkpoint structure, plugin path references, and license inclusion. The Git fixture uses a temporary repository and local identity only. Symlink checks are skipped explicitly if the OS does not permit symlink creation; traversal checks still run.

No package installation, vendor API key, subscription, model call or application deployment is required. The action runners download/select Python as needed. The action versions follow the official actions/checkout and actions/setup-python documentation checked during this update.

CI does not establish model compliance, actual host discovery, remote web link availability, all Markdown anchor validity, every operating system/version, or factual truth inside a checkpoint. Native Claude plugin validation can also be run locally with `claude plugin validate .`; it is not a dependency of the hosted workflow.

## Local equivalent

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

Use `python` instead of `python3` where required. Run from the repository root. When a test fails, fix the issue or disclose an actual platform constraint; do not turn a failing check into a success with `continue-on-error`.

For updates, keep the root LICENSE and bundled skill LICENSE identical. Update the supported metadata checks if adding a legitimate Agent Skills field. Installation of the standalone skill must retain its license and all referenced resources.

## Sources

- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions)
- [actions/checkout](https://github.com/actions/checkout)
- [actions/setup-python](https://github.com/actions/setup-python)

## Release publication

The separate Publish release workflow checks versioned notes and the package suite before publishing. Read permission is the default; only its publishing job receives contents-write permission. It accepts version tags and manual dispatch, with a narrow v0.1.0 bootstrap when its workflow file changes on main. Existing releases are left unchanged. The [initial publication run](https://github.com/kristianrolando/cross-agent-handoff/actions/runs/41429718374) completed successfully. See docs/releasing.md for future releases.
