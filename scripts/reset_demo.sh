#!/usr/bin/env bash
# Reset the demo repository on GitHub to the start of the demo.
#
# Moves `main` back to the tag `demo-start`, recreates the two demo branches
# on top of it, and deletes every other branch. GitHub settings stay as they
# are: the environments and the reviewer on `production`. Old pull requests
# stay closed or merged; the demo opens new ones.
#
# Run it from a clone of the demo repository: scripts/reset_demo.sh
set -euo pipefail

readonly BASELINE=demo-start
readonly DEMO_BRANCHES=(fix/threshold data/new-batch)
# Workflows a push to main can start. The reset push changes code and
# datasets/**, so Release and CT would run, and CT would commit to the
# registry on top of the baseline.
readonly MAIN_WORKFLOWS=(Release CT)
# Time for GitHub to process the push while the workflows are disabled.
readonly PUSH_SETTLE_SECONDS=15

enable_main_workflows() {
  for workflow in "${MAIN_WORKFLOWS[@]}"; do
    gh workflow enable "$workflow"
  done
}

reset_main() {
  for workflow in "${MAIN_WORKFLOWS[@]}"; do
    gh workflow disable "$workflow"
  done
  trap enable_main_workflows EXIT
  git push --force origin "$BASELINE^{commit}:refs/heads/main"
  sleep "$PUSH_SETTLE_SECONDS"
  enable_main_workflows
  trap - EXIT
}

recreate_demo_branches() {
  local worktree
  worktree=$(mktemp -d)
  git worktree add --quiet --detach "$worktree" "$BASELINE"
  (
    cd "$worktree"
    # A code change with a bug.
    git switch --quiet --force-create fix/threshold "$BASELINE"
    perl -pi -e 's/x >= threshold/x <= threshold/' src/ci_cd_ct_demo/model.py
    git commit --quiet -am "fix: compare x with the threshold"
    # New, shifted data.
    git switch --quiet --force-create data/new-batch "$BASELINE"
    uv run scripts/make_data.py --shift 2 --seed 1
    git commit --quiet -am "data: add the latest labelled batch"
    git switch --quiet --detach
  )
  git worktree remove --force "$worktree"
  git push --force origin "${DEMO_BRANCHES[@]}"
}

delete_other_branches() {
  local branch
  git fetch --quiet --prune origin
  for branch in $(git branch -r --format='%(refname:lstrip=3)'); do
    case "$branch" in
      HEAD | main | fix/threshold | data/new-batch) ;;
      *) git push origin --delete "$branch" ;;
    esac
  done
}

# A run from the last class may still wait for approval on production, and
# approving it later would deploy a model the reset registry no longer has.
cancel_unfinished_runs() {
  local status run_id
  for status in waiting queued in_progress; do
    for run_id in $(gh run list --status "$status" --json databaseId -q '.[].databaseId'); do
      gh run cancel "$run_id"
    done
  done
}

main() {
  git fetch --quiet --tags origin
  cancel_unfinished_runs
  reset_main
  recreate_demo_branches
  delete_other_branches
  echo "Reset done. To match it locally: git switch main && git reset --hard origin/main"
}

main "$@"
