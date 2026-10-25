# Operations

## Safe use
- use synthetic/non-sensitive test data where possible
- keep model/runtime experiments isolated
- record dependency versions for reproducibility

## Before reusing code in Butler
- run tests
- inspect secrets/config
- inspect persistence
- remove hard-coded paths
- add auth/audit hooks as required

## Archival
Tag known-good experimental milestones before major rewrites.
