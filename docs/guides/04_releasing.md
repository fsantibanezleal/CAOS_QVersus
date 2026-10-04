# 04 · Releasing

## Versions

The display version `X.XX.XXX` (major, minor, patch, zero-padded) lives in `VERSION`, in
`qversus.__version__` and in the newest `CHANGELOG.md` heading; `pyproject.toml` carries the PEP 440 form with
the zeros dropped (`0.01.000` is `0.1.0`). CI fails when they disagree. The git tag is `vX.XX.XXX`. Stay in
`0.x` while the contracts may still change.

Bump by the nature of the change: a new capability is a major (after 1.0) or a minor (before 1.0); a completed
feature or a behaviour change is a minor; everything else is a patch.

## Flow

1. Work lands on `develop` through pull requests from `task/<slug>` branches.
2. Bump `VERSION`, `pyproject.toml`, `qversus/__init__.py` and add the `CHANGELOG.md` section, in one commit.
3. Pull request `develop` to `main`; merge when CI is green.
4. Tag `main`: `git tag vX.XX.XXX && git push origin vX.XX.XXX`.
5. Publish a GitHub release for the tag (`gh release create vX.XX.XXX --notes-from-tag` or with notes). The
   `publish-pypi.yml` workflow checks that the tag, `VERSION` and `pyproject.toml` agree, builds the sdist and
   the wheel, and uploads them by PyPI trusted publishing (OIDC): no token is stored anywhere.
6. Verify in a clean environment: `pip install qversus==X.Y.Z` and run the quick start.

## Trusted publishing (one-time, per project)

On pypi.org, the project owner registers a (pending) trusted publisher with: project `qversus`, owner
`fsantibanezleal`, repository `CAOS_QVersus`, workflow `publish-pypi.yml`, environment `pypi`. The workflow
file name is part of the identity PyPI checks: renaming the file breaks publishing with an `invalid-publisher`
error.
