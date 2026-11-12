# Releasing Plotform

This project uses GitHub Actions and PyPI **trusted publishing** (OIDC). Do not
store long-lived PyPI tokens in the repository.

## 1. Validate the source

Before creating a release:

```bash
pytest
ruff check .
ruff format --check .
python -m build
python tools/check_sdist.py
```

Install the wheel into a clean environment and run a small import and plotting
smoke test. The CI workflow must also be green.

## 2. Push the release branch

The repository remote is `https://github.com/Econ01/plotform.git`.

If using the `release/0.1.0` branch:

```bash
git push -u origin release/0.1.0
```

Open a pull request into `main`, review the diff and CI checks, and merge when
ready. A direct push to `main` is also possible for a solo project, but the pull
request provides a useful release review.

## 3. Create GitHub environments

In **Settings → Environments**, create:

- `testpypi`
- `pypi`

For the first production release, require manual approval on the `pypi`
environment so publication cannot happen accidentally.

## 4. Configure TestPyPI trusted publishing

Sign in to TestPyPI and add a **pending trusted publisher** with exactly:

- PyPI project name: `plotform`
- Owner: `Econ01`
- Repository name: `plotform`
- Workflow name: `release.yml`
- Environment name: `testpypi`

If a TestPyPI project already exists, add the publisher under its publishing
settings instead.

## 5. Configure production PyPI trusted publishing

On production PyPI, add the same publisher identity, except:

- Environment name: `pypi`

The workflow filename and environment names must match exactly. GitHub Actions
uses these values when requesting an OIDC token.

## 6. Publish to TestPyPI

In the GitHub repository, open **Actions → Release → Run workflow** and run the
workflow on the release branch. A manual workflow run publishes only to
TestPyPI; production publication happens through a GitHub release.

Then create a clean environment and install:

```bash
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  plotform
```

The extra index supplies dependencies such as Matplotlib and NumPy that may not
be available on TestPyPI.

Verify:

```python
import plotform as tm

assert tm.__version__ == "0.1.0"
tm.apply_theme()
```

Run a small plotting example as well.

## 7. Create the production release

After TestPyPI validation:

1. Ensure `pyproject.toml` contains version `0.1.0`.
2. Update `CHANGELOG.md` if needed.
3. Create and push tag `v0.1.0`:

   ```bash
   git tag -a v0.1.0 -m "Plotform 0.1.0"
   git push origin v0.1.0
   ```

4. In GitHub, choose **Releases → Draft a new release**, select `v0.1.0`, add
   the changelog notes, and publish.
5. The Release workflow checks the tag, builds the distributions, and publishes
   to production PyPI through the `pypi` environment.
6. Approve the production environment if protection is enabled.

## 8. Verify the public installation

In another clean environment:

```bash
python -m pip install plotform
python -c "import plotform; print(plotform.__version__)"
```

Finally, add the repository description, topics, and PyPI link in GitHub's About
section. The README already contains CI, PyPI, Python, and license badges.
