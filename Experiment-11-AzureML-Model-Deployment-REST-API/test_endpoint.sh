#!/usr/bin/env bash
# Test the deployed Pass/Fail classifier endpoint (Experiment 11).
#
# SCORING_URI: printed by deploy.py after deployment, or shown on the
#   endpoint's Consume tab in Azure ML Studio.
# PRIMARY_KEY: fetch the primary key from the endpoint's Consume tab in
#   Azure ML Studio (or via the CLI) at test time. Never commit a real key.
#
# Fill in both placeholders below, then run: ./test_endpoint.sh

SCORING_URI="<scoring-uri>"
PRIMARY_KEY="<primary-key>"

curl -X POST "$SCORING_URI" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PRIMARY_KEY" \
  -d '{"data": [[78, 85, 82]]}'
echo
