# Contributing

This project is based on the PyTalos automation framework template.

## Bug Reports

When opening new issues or commenting on existing issues, please make sure
discussions are related to concrete technical issues.

It's imperative that issue reports outline the steps to reproduce the defect.
Please provide concise reproducible test cases and describe what results you
are seeing and what results you expect.

Issues shouldn't be used for support. Please address questions through your
team's usual communication channels.

## Code Contributions

### Step 1: Fork and clone

Fork the project on your Git host and check out your copy locally.

```shell
git clone <your-repo-url>
cd <project-folder>
```

### Step 2: Branch

Create a feature branch and start hacking:

```shell
git checkout -b my-feature-branch
```

### Step 3: Commit

Write good commit messages: a commit message should describe what changed,
why, and reference issues fixed (if any).

```shell
git commit -m "a very good commit message"
```

### Step 4: Pull Request

Go to your Git host and create a new pull request from your feature branch
to the main development branch.

Fill in the Pull Request description clearly and efficiently.

## Notes

- Do not commit secrets, credentials or environment-specific data.
  Use `.env` (git-ignored) for sensitive values.
- Test data per environment belongs in `settings/profiles/<env>/datas.json`.
- Custom step definitions go in `test/steps/`; shared helpers in
  `test/helpers/`; hooks in `test/helpers/hooks.py`.
