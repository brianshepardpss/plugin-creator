#!/bin/sh
# Wait for the review app, then hit the export endpoint once.
set -eu
for i in $(seq 1 600); do
  if curl -sf "$REVIEW_APP_URL/healthz" >/dev/null; then
    curl -sf "$REVIEW_APP_URL/export.csv" >/dev/null && exit 0
  fi
  echo "waiting for review app (attempt $i/600)"
  sleep 1
done
exit 1
