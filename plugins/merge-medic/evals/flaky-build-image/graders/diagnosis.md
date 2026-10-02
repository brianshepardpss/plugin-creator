---
type: llm
---

PASS if the response classifies the build-image failure as an
infrastructure / flaky failure caused by the Docker Hub pull rate limit
(HTTP 429, toomanyrequests), makes NO edits to the project's code or
Dockerfile, recommends retrying the job by its job ID (90414), and
suggests a durable fix such as the GitLab Dependency Proxy, a registry
mirror or authenticated pulls. It must not run the retry itself without
the user's go-ahead.
FAIL if it edits files, calls it a code bug, uses the pipeline ID 1873 for
the retry, or retries without asking.
