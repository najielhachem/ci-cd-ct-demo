# CI, CD and CT demo runbook

Instructor notes for a short live demo in the session on releasing new models,
right after the CI, CD and CT slides. Students watch the GitHub Actions tab.

The model and the registry are dummies, so every run takes seconds:

- The model is one threshold on one feature `x`
  ([`model.py`](src/ci_cd_ct_demo/model.py)).
- The registry is [`registry.json`](registry.json): versions and the
  aliases `champion` and `challenger`, as in the session-20 lab.
- [`deploy.py`](scripts/deploy.py) only prints what it would deploy, and which
  `champion` the service would load at startup.

## What it shows

| Workflow | Triggered by | Runs | Slide concept |
|---|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | a pull request; called by Release | ruff, pytest on code, data and model, `uv build` | CI tests and builds the code |
| [`release.yml`](.github/workflows/release.yml) | a push to `main` that changes code | CI, then Deploy to `staging`, then Deploy to `production` | CD delivers what CI built |
| [`ct.yml`](.github/workflows/ct.yml) | new data pushed to `main`; every Monday; the **Run workflow** button | `train.py`, the gate in `promote.py`, a commit of `registry.json`; if the gate promoted, Deploy to `staging`, then `production` | CT retrains when the data changes |
| [`deploy.yml`](.github/workflows/deploy.yml) | called by Release and CT | `deploy.py` in one environment: a new wheel, or a restart of the running build | the deploy step both share |

Each of Release and CT is one run with one graph, the way production ML
platforms chain their stages. Production waits for a reviewer in both.

The point to land: a code change goes through CI and CD; a data change goes
through CT, which ends with its own rollout. A new `champion` reaches users
with no new build.

## Before class

- [ ] Create a throwaway GitHub repository and push this folder's contents to
      its root. GitHub only runs workflows from the repository root, so they
      don't run inside the course repo.
      ```bash
      cp -R material/modules/05-deployment-and-monitoring/demos/ci-cd-ct-demo ~/ci-cd-ct-demo
      cd ~/ci-cd-ct-demo && rm -rf .venv .pytest_cache .ruff_cache
      git init -b main && git add . && git commit -m "feat: initial demo"
      gh repo create ci-cd-ct-demo --private --source . --push
      ```
- [ ] Open the Actions tab. The first push runs CI, then CD. Check both pass.
- [ ] In Settings > Environments > `production`, add yourself as a required
      reviewer. Release and CT then wait for your approval before production:
      the "approved change" of the CD slide. GitHub creates `staging` and
      `production` on the first run that uses them.
- [ ] Prepare the two branches below, so nothing is typed under pressure.
      Push them, but don't open the pull requests yet.
      ```bash
      # A code change with a bug
      git switch -c fix/threshold main
      sed -i '' 's/x >= threshold/x <= threshold/' src/ci_cd_ct_demo/model.py
      git commit -am "fix: compare x with the threshold" && git push -u origin fix/threshold

      # New, shifted data
      git switch -c data/new-batch main
      uv run scripts/make_data.py --shift 2 --seed 1
      git commit -am "data: add the latest labelled batch" && git push -u origin data/new-batch
      git switch main
      ```
- [ ] Keep a recording of the four steps as a fallback: the demo needs the
      network.

## The demo

### 0. The pipeline in the code

Before any run, open the workflow files and show the shape they build:

```text
PR          CI (lint, tests, build)                      ← check on the PR

Release     ci ──▶ staging ──▶ [approve] ──▶ production   ← one run, same wheel all the way
(code on main)

CT          train-and-gate ──▶ staging ──▶ [approve] ──▶ production
(data / cron / button)   │  commits registry.json      no new build: restarts the running build
                         └─ no promotion → staging and production show as skipped
```

- [`release.yml`](.github/workflows/release.yml): three jobs, each a `uses:`
  of another workflow, chained by `needs:`. CI is the first stage of the
  release, not a separate trigger.
- [`deploy.yml`](.github/workflows/deploy.yml): one deploy for one
  `environment`. The required reviewer on `production` is the approval step.
- [`ct.yml`](.github/workflows/ct.yml): the gate's `promoted` output decides
  whether `staging` runs, and `new-build: false` deploys the new champion
  with the build already running.

### 1. CI on a pull request

Open a pull request from `fix/threshold`. CI runs and fails on the two
model tests in `tests/test_model.py`; the data and registry tests pass.

- Show the log: lint, then tests on code, data and model, as on the "What CI
  tests" slide.
- Revert the bug on the branch (`git revert HEAD && git push`). CI runs again
  and passes. Close the pull request without merging, or merge the revert.

### 2. CD after a merge

Make any small code change on a branch (a docstring), open a pull request,
let CI pass, and merge it.

- Release runs on `main`. Open its graph: `ci`, then `staging`, then
  `production`, waiting for your approval.
- Show the `staging` log: it deploys the wheel `ci` built in the same run, not
  a new build, and says the service loads `champion -> v1`. Approve
  `production`: the same wheel goes out.
- The pull request's CI run and Release are two runs: the merge makes a new
  commit, and Release tests that commit before shipping it.

### 3. CT on new data

Open a pull request from `data/new-batch`.

- CI runs the data tests on the new files, as DTU's CML does on a data
  pull request.
- Merge it. CT starts; Release doesn't, because `release.yml` ignores
  `datasets/**`.
- Show the CT log: the challenger v2 scores about 0.94 on the new holdout,
  the champion v1 about 0.56. The gate moves `champion` to v2.
- Show the commit `ct: train a challenger and run the gate` on `main`, and
  `registry.json` in it.
- Open the CT graph: `train-and-gate`, then `staging`, then `production`,
  waiting for your approval. The `staging` log says "no new build: restarting
  the running build" and loads `champion -> v2`. Approve `production`: a new
  model reaches users with no new build.

### 4. A CT run with nothing new

Click **Run workflow** on CT. It trains v3 on the same data; v3 ties with
v2, the gain is below `--min-gain 0.02`, and `champion` stays v2. The graph
shows `staging` and `production` skipped: nothing to roll out.

- This is the schedule's weak spot from the triggers slide: it retrains when
  nothing changed, and the gate keeps it from shipping.

## What to say about the shortcuts

- The holdout here is the newest batch's own holdout split: recent and
  labelled, as the gate slides ask. In real life it comes after the
  challenger's training window and the label delay.
- CT here is triggered by new data. A drift trigger would run the drift check
  of the end-to-end demo first and start CT only when it fails.
- Real CD pushes an image and restarts a service. Real CT trains in its own
  pipeline and writes to MLflow, not to a JSON file in the repository.

## Pitfalls

- Commits pushed with the workflow's `GITHUB_TOKEN` start no other workflow.
  That is why CT's registry commit doesn't start Release, and it's GitHub's
  rule, not something the workflows set.
- `schedule` only uses the workflow file on the default branch, `main`.
  Editing CT's cron on a branch changes nothing until merged.
- Scheduled runs can start late, and GitHub disables them in a repository
  with no activity for 60 days. Use the **Run workflow** button in class.
- If CT fails on `git push` with a 403, set Settings > Actions > General >
  Workflow permissions to "Read and write".
- Run the scripts from the repository root: their default paths are relative
  to it.

## Reset after class

Run [`scripts/reset_demo.sh`](scripts/reset_demo.sh) from a clone of the
throwaway repository, with `gh` logged in. It brings the repository back to
the end of "Before class", so the demo can run again:

- Runs still waiting, such as a CT run waiting for production approval, are
  cancelled.
- `main` goes back to the tag `demo-start`: `registry.json` holds only v1.
  Release and CT are disabled during that push, or it would start them.
- `fix/threshold` and `data/new-batch` are recreated on top of it, with the
  commands above.
- Every other branch is deleted.
- The environments and the reviewer on `production` are GitHub settings, not
  git, and stay as they are.

The tag is made once, when the repository is created:
`git tag demo-start && git push origin demo-start`. Move it when the demo
itself changes.
