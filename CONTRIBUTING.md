# Contributing to `Krux` firmware

The development of `Krux` firmware is FOSS and community-effort-based and
welcomes contributions from anyone. We are excited you are interested in
helping us bring sovereign and private self-custody to everyone.

We welcome contributions in many forms, including bug reports, feature
requests, code contributions, and documentation improvements, from any
contributors with any level of experience or expertise.

Besides that, we ask that you respect others and follow the process
outlined in this document.

---

## Read the docs carefully

We have a deep and a concise
[documentation for users](https://selfcustody.github.io/krux). Besides
that, not all of them read the documentation properly.

As a developer, don't do that. Read carefully the current documentation
and, if you think it isn't sufficient for the utmost standards, please
[make a PR](https://github.com/selfcustody/krux/pulls/new); it's a very
`good first issue` and a welcomed contribution.

---

## Non `Krux` firmware contributions

The `Krux` growth in the Bitcoin ecosystem is due to developments beyond firmware.
They're built from real, material, and daily use cases from our beloved
community of kruxers. While we love that, we cannot be responsible for any
development made by our users.

Our developers and contributors are listed in both [krux contributors list](https://github.com/selfcustody/krux/contributors)
and [krux-installer contributors list](https://github.com/selfcustody/krux-installer/contributors)
.

---

## Communications Channels

The primary communication channel is the [GitHub repository](https://github.com/selfcustody/krux)
.

---

## Contribution Workflow

The contribution workflow is designed to facilitate cooperation and ensure a
high level of quality in the project and not to enforce any type of dogmatic
procedure on creative level. The process is as follows:

To contribute a patch, the workflow is as follows:

  1. Fork Repository
  2. Create topic branch
  3. Commit patches
  4. Push to fork
  5. Open PR
  6. Peer review

### Fork Repository

[Fork the repository](https://github.com/selfcustody/krux), so you can create
a remote repository fork for your changes. Then clone it:

```bash
git clone git@github.com:<user>/krux.git
```

Then follow the initial procedures described on [README.md](./README.md).

### Create a topic branch

You always start with a `main` branch initialized. While the
community of developers standardized this as the **stable** development branch
(some projects could use the `master` branch for historical reasons),
the `Krux` firmware team stated the first one as the **stable** branch and the
`develop` as the branch that all developers should start from and experiment with.
After you have had fun and discovered things, create a properly named branch to
identify when we release:

> Bitcoin related projects, like bdk, pdk and floresta use
`<type>/<name>` named branches.
 

```bash
main -> develop -> chore/task-stuff
                -> ci/job-stuff
                -> docs/info-new
                ...
```

So, in command line you could do this, keeping in mind what you will do in
the PR:

```bash
git checkout -b <type/name>
```

### Named branches

A patch is a set of changes (patches or `diffs`) that you propose to `Krux`
firmware developers to include in `develop` branch as a (set) of commits.

In general commits should be atomic and `diffs` should be easy to read.
For this reason do not mix any formatting fixes or code moves with actual code
changes. Further, each commit, individually, should compile and
pass tests whenever possible, in order to ensure that `git bisect` and other automated tools
function properly.

When adding a new feature, ensure that it is covered by functional tests where
possible. Avoiding this will create uncovered code.

When refactoring, structure your PR to make it easy to review and don't
hesitate to split it into multiple small, focused PRs.

---

## Commit patches

These [guidelines](https://chris.beams.io/posts/git-commit/) should be kept in
mind. Commit messages follow the
["Conventional Commits 1.0.0"](https://www.conventionalcommits.org/en/v1.0.0/)
to make commit histories easier to read by humans and automated tools.
The types of commits we use are:

- `chore`: maintenance tasks (mostly lint, format);
- `ci`: continuous integration (generally `.github/**` files);
- `docs`: documentation changes (`*.md` files);
- `feat`: new feature (`src/**`, imperatively -- it's recommended that `test` and
  `docs` are accompanied in the PR);
- `fix`: bug fix (see if it could break changes -- `!`, it's recommended that
  `test` and `docs` are accompanied);
- `git`: used when changing some git stuffs;
- `i18n`: mostly addtion/fix of locale words/expressions;
- `refactor`: code change that neither fixes a bug nor adds a feature (could be
  a tiny change or a entire code-base refactor -- in krux refactor is the
  first);
- `style`: formatting, missing semi colons, ui colors, icons, etc; no functional
  code change;
- `test`: adding missing tests or correcting existing tests;

---

## Push to fork

With commits done, it's time to push to **your fork/branch:

```bash
# first time
git push --set-upstream <user> <branch>
```

---

## Open PR

After pushed to your fork/branch, github will show -- on your fork branch page --
a button to Open PR. After click, you will be redirected to an editor with some
templated structure. Fill the fields and open the PR. For WIP (Work In Progress)
PRs we recommend to open a Draft PR.

---

## Peer review

To make sure our code has the highest quality and is maintainable for
posterity, we have a thorough peer review process, where pull requests need
to be reviewed by at least one maintainer, and must not have any outstanding
comment from regular contributors (unless one of maintainers recognizes the
rationale).

### Conceptual Review

A review can be a conceptual review, where the reviewer leaves a comment:

- Concept `cACK`: "I agree with the general goal of this pull request";
- Approach `nACK`: "I do (not) agree with the approach of this change";
- Untested `utACK`: "I didn't test, but ACK";
- Tested `tACK`: "I tested and ACKed".

A nACK needs to include a rationale why the change is not worthwhile.
nACKs without accompanying reasoning may be disregarded.

### Code Review

After conceptual agreement on the change, code review can be provided.
A review begins with ACK `BRANCH_COMMIT`, where `BRANCH_COMMIT` is the top of
the PR branch, followed by a description of how the reviewer did the review.
The following language is used within pull request comments:

- Tested ACK:

> tACK `babc00fe`. I have tested the code", involving change-specific manual
testing and in case it was not obvious how the manual testing was done. nit:
maybe it could be described in a `docs` commit sharing your intentions.

-- Untested ACK:

> utACK `babc00fe`.
"I have not tested the code, but I have reviewed it and it looks OK, I agree
it can be merged".

A "nit" refers to a trivial, often non-blocking issue.

Project maintainers reserve the right to weigh the opinions of peer reviewers
using common sense judgement and may also weigh based on merit. Reviewers that
have demonstrated a deeper commitment and understanding of the project over
time or who have clear domain expertise may naturally have more weight, as one
would expect in all walks of life.

```markdown
tACK c00febab

I liked the approach! Just some minor nit:

- the line 3 has a typo on comment: `Helllo` should be `Hello`. So 
I suggest this change:

<diff>
- # The resulting Helllo
+ # The resulting Hello
result = "Hello"
</diff>

Besides that, is a neat work @user!
```

---

## Coding Conventions

There are a few rules to make sure the code is readable and maintainable.
Most of them are checked by `poetry run poe lint` and `poetry run poe format`,
and are enforced by CI.

### Python

```python
# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

# ...
class Foo:
    """Some awesome comment"""

    def func(self):
        """Some awesome comment"""
        pass
```


#### New features

All new features require testing. Tests should be unique and self-describing.
When it comes error handling, we prefer exact and meaningful error handling
to deliver consumers (developers and users) an accurate error that describes
exactly what happened wrong. Instead of:

```python
# A function that concatenate a int and a float into a str
def foo(
    bar: int,
    baz: float,
) -> str:
    str(bar) + str(baz)
```

prefer:

```python
# A function that concatenate a int and a float into a str and why do that
# for a good and reasonable reason that you should discuss with other developers
# keep in mind that we're coding for micropython
def foo(bar, baz):
    """Serialize an int with a float into new str"""
    if not isinstance(bar, int):
        raise ValueError("Expected bar to be an int")

    if not isinstance(baz, float):
        raise ValueError("Expected baz to be a float")

    bar_str = str(bar)
    baz_str = str(baz)

    # We need to concatenate to be compliant
    return bar_str + baz_str
```

### Markdown

Markdown files are linted too. This keeps the `*.md` files standardized and
properly formatted for any code editor. Some of the currently applied rules
enforced by CI:

```markdown
- \# heading should be toplevel heading;
- lines should be compact: 80 chars per line;
- raw links aren't allowed, use the [text](link) format instead;
- items should follow correct indentation.
```

---

## Testing

We expect to have 95% test coverage for each PR. We have a few types of tests
that you can run using `poetry run poe test`. See more with `poetry run poe`.

---

## Release

Once a maintainer and the contributors decide we have a stable enough `develop`
with sufficient features, we will merge the `develop` branch with the `main`
at that point. From this point, all new changes will go in the next release.
After sufficient testing and making sure we don't have bugs left, this branch 
will be released by one of the maintainers.

The release will have pre-built binaries available on github's asset page.
They **must** be OpenSSL signed by [odudex](mailto:odudex@proton.me) --
verifiable with [`selfcustody.pem`](./selfcustody.pem), and have a `zip`
accompanied with `zip.sha256.txt` release assets.

If we find bugs on a release, the fix may be backported and a new minor release
may be released. This is done by merging fixes on top of the release branch.
And then performing another release on that branch.

If you found any security issue, please read [`SECURITY.md`](https://github.com/selfcustody/krux/security),
we're glad you have the choice to grow this community in a cypherpunk way.

If you have any questions related to this process or the codebase in general,
don't hesitate to reach out to us. We are happy to help newcomers in their
amazing journey. Overall, have fun :)
