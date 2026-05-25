# Contributing to Krux firmware

Krux firmware is free and open-source software, built as a community effort.
We welcome contributions of any kind: bug reports, feature requests, code,
and documentation, from contributors of any experience level. We only ask
that you respect others and follow the process described here.

---

## Read the documentation

We maintain detailed
[user documentation](https://selfcustody.github.io/krux). Please read it
carefully before contributing. If you find it incomplete or unclear,
improving it is a welcome contribution and a good first issue.

---

## Communication channels

The primary channel is the
[GitHub repository](https://github.com/selfcustody/krux). Contributors are
credited in the
[krux](https://github.com/selfcustody/krux/contributors) and
[krux-installer](https://github.com/selfcustody/krux-installer/contributors)
contributor lists.

---

## Contribution workflow

The workflow is meant to support cooperation and keep quality high, not to
impose rigid procedure. To contribute a patch:

  1. Fork the repository
  2. Create a topic branch
  3. Commit your changes
  4. Push to your fork
  5. Open a pull request
  6. Address peer review

### Fork the repository

[Fork the repository](https://github.com/selfcustody/krux) and clone your
fork:

```bash
git clone git@github.com:<user>/krux.git
```

Then follow the setup steps in [README.md](./README.md).

### Create a topic branch

`main` is the stable branch and `develop` is the integration branch that all
development starts from. Create your topic branch off `develop`, using a
`<type>/<name>` convention (as used by Bitcoin projects such as bdk and
floresta):

```bash
main -> develop -> chore/task-stuff
                -> ci/job-stuff
                -> docs/info-new
```

```bash
git checkout develop
git checkout -b <type>/<name>
```

### Commit your changes

Commits should be atomic and their diffs easy to read. Do not mix formatting
changes or code moves with functional changes. Each commit should build and
pass tests where possible, so that `git bisect` and other tools work
reliably. New features should be covered by tests. When refactoring, keep
pull requests focused and split large changes into smaller ones.

Follow these
[commit message guidelines](https://chris.beams.io/posts/git-commit/) and the
["Conventional Commits 1.0.0"](https://www.conventionalcommits.org/en/v1.0.0/)
specification. The commit types we use are:

- `chore`: maintenance tasks (mostly lint and format);
- `ci`: continuous integration (generally `.github/**` files);
- `docs`: documentation changes (`*.md` files);
- `feat`: new feature (`src/**`; tests and docs should accompany it);
- `fix`: bug fix (use `!` for breaking changes; tests and docs should
  accompany it);
- `i18n`: addition or fix of locale strings;
- `refactor`: change that neither fixes a bug nor adds a feature;
- `style`: formatting, colors, icons, etc., with no functional change;
- `test`: adding or correcting tests.

### Push to your fork

```bash
# first push
git push --set-upstream origin <branch>
```

### Open a pull request

After pushing, GitHub shows an "Open pull request" button on your fork's
branch page. Fill in the template and open the PR against `develop`. For work
in progress, open a Draft PR.

### Peer review

To keep the codebase high quality and maintainable, every pull request is
reviewed by at least one maintainer and should have no unresolved comments
from contributors (unless a maintainer accepts the rationale).

Reviews are expressed with acknowledgement (ACK) tags:

- `cACK`: concept ACK, I agree with the goal of this PR;
- `nACK`: I disagree with the change (must include a rationale; an
  unexplained `nACK` may be disregarded);
- `utACK`: untested ACK, I reviewed the code but did not test it;
- `tACK`: tested ACK, I reviewed and tested the code.

A code review references the branch commit being reviewed. A "nit" is a
trivial, usually non-blocking issue. For example:

```markdown
tACK c00febab

I like the approach! One nit: line 3 has a typo in a comment,
`Helllo` should be `Hello`:

- # The resulting Helllo
+ # The resulting Hello

Nice work, @user!
```

Maintainers weigh reviewer opinions using their judgement, giving more weight
to reviewers with proven commitment or domain expertise.

---

## Coding conventions

A few rules keep the code readable and maintainable. Most are checked by
`poetry run poe lint` and `poetry run poe format`, and enforced by CI.

### Python

Every source file starts with the license header:

```python
# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors
```

Prefer explicit, meaningful error handling that tells developers and users
exactly what went wrong. Keep in mind that Krux runs on MicroPython. For
example:

```python
def foo(bar, baz):
    """Serialize an int and a float into a new str"""
    if not isinstance(bar, int):
        raise ValueError("Expected bar to be an int")

    if not isinstance(baz, float):
        raise ValueError("Expected baz to be a float")

    return str(bar) + str(baz)
```

### Markdown

Markdown files are linted to stay consistent across editors. Some of the
rules enforced by CI:

- the first heading should be a top-level heading;
- keep lines compact, around 80 characters;
- use the `[text](link)` format instead of raw links;
- follow correct list indentation.

---

## Testing

We aim for high test coverage (95% or more) on each PR. Run the tests with
`poetry run poe test`, and list all available tasks with `poetry run poe`.

---

## Release

When maintainers and contributors agree that `develop` is stable and has
enough features, `develop` is merged into `main`. After further testing, a
maintainer publishes the release.

Releases include pre-built binaries on the GitHub assets page. They are
OpenSSL signed by [odudex](mailto:odudex@proton.me) and verifiable with
[`selfcustody.pem`](./selfcustody.pem), and ship as a `zip` accompanied by a
`zip.sha256.txt` file.

If bugs are found in a release, fixes may be backported on top of the release
branch and published as a new minor release.

To report a security issue, please use the repository's
[security advisories](https://github.com/selfcustody/krux/security).

If you have questions about this process or the codebase, don't hesitate to
reach out. We are happy to help newcomers. Have fun!
