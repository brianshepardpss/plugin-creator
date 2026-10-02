# glab notes for Merge Medic

Read the section a step points you to; do not read this whole file up front.
Verified against glab v1.120.0 docs (2026-10).

## Hosts (self-managed first)

- glab picks the host from the git remote of the current directory. Run
  commands inside the repo and it targets the right instance, including
  self-managed hosts and GitLab Dedicated.
- `GITLAB_HOST` overrides the host (useful outside a repo).
  `glab api --hostname <host> ...` targets a host for one call.
- `-R <group/project>` or `-R https://<host>/<group>/<project>` targets
  another project. A full URL also selects its host.
- Log in: `glab auth login --hostname <host>` (interactive, `--web`,
  `--device` on GitLab 17.9+, or `--stdin` with a personal access token).
  Token scopes: `api` and `write_repository`.
- Private CA: `glab config set ca_cert /path/ca.pem --host <host>` (or
  `GLAB_CA_CERT`). Mutual TLS: `client_cert` / `client_key`. Do not suggest
  `skip_tls_verify` except for throwaway test instances, and say why.
- Several instances: `glab auth status --all` lists them.

## Older glab (flags missing)

`glab ci get --merge-request` / `--status` are recent. If glab rejects them:

```
glab api projects/:id/merge_requests/<iid>/pipelines        # newest first; take [0].id
glab api "projects/:id/pipelines/<pipeline-id>/jobs?scope[]=failed&per_page=100" \
  | python3 <skill>/scripts/failed_jobs.py -
```

Draft review comments need glab 1.119.0+ (`mr note create --draft`,
`mr note publish`). `mr note list`/`resolve` need 1.90+. Suggest
`brew upgrade glab` (or the user's package manager) rather than working
around it.

## Pipelines that hide the failure

- **Parent-child / multi-project pipelines:** a failed job with no log of
  its own is usually a trigger (bridge) job. List bridges:
  `glab api projects/:id/pipelines/<id>/bridges`, take
  `downstream_pipeline.id` (and its `project_id`), then
  `glab ci get -p <child-id> --status failed -F json` (add `-R` for
  another project) and continue from step 2.
- **Merged-results pipelines:** the ref is `refs/merge-requests/<iid>/merge`;
  the failure can come from the target branch. Check whether the failing
  test touches files changed in the MR before editing.
- **YAML errors:** the pipeline has `yaml_errors` and no jobs. Run
  `glab ci lint` (it validates against the user's own instance), fix, lint
  again, then push.

## Fix recipes

**Docker Hub 429 (`toomanyrequests`, pull rate limit).** Retry the job ID
first. Durable fix: pull through the GitLab Dependency Proxy.
- `image:` lines: `image: ${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/python:3.12-slim`
  (the runner authenticates automatically).
- `FROM` lines in a Dockerfile built in CI: log in first with
  `echo "$CI_DEPENDENCY_PROXY_PASSWORD" | docker login "$CI_DEPENDENCY_PROXY_SERVER" -u "$CI_DEPENDENCY_PROXY_USER" --password-stdin`
  and pass the prefix as a build arg
  (`ARG PROXY=docker.io` / `FROM ${PROXY}/library/python:3.12-slim`).
- The Dependency Proxy must be enabled for the group (Settings > Packages
  and registries). On self-managed it also needs the admin to enable it;
  otherwise suggest an internal registry mirror or authenticated pulls.

**Exit code 137 / `Killed`.** The kernel killed the process for memory.
Options: run fewer tests per job (`parallel:` with test splitting), lower
worker count (`pytest -n`, Jest `--maxWorkers`), set
`NODE_OPTIONS=--max-old-space-size=...` for Node, or a runner tag with more
memory. Ask which the team prefers.

**Job timeout.** `execution took longer than <limit>`. Look for a polling
loop or a hung service in the excerpt first. Changing `timeout:` is a team
decision; propose it, do not do it silently.

**npm ERESOLVE.** Align the conflicting versions (upgrade the dependent
package to a release that supports the installed peer, or pin the peer).
`--legacy-peer-deps` only with the user's agreement, and record why in the
commit message.

## Limits

- gitlab.com: 2,000 authenticated API requests per minute per user; note
  creation 60 per minute; pipeline creation 25 per minute per project, user
  and commit. Self-managed: whatever the admin set. Merge Medic makes one
  `ci get` per run plus one trace call per failed job.
- Job logs larger than the instance's log limit end with
  `Job's log exceeded limit`; the error may be in the truncated part. Say so
  and suggest reproducing locally.
