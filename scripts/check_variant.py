# /// script
# requires-python = ">=3.14"
# dependencies = ["copier==9.18.2"]
# ///
"""Render one option combination of the template and run the generated project's own checks.

The same script backs `just test` locally and every job of the CI matrix, so they cannot drift.

    uv run scripts/check_variant.py api-db            # render + setup + check + pre-commit
    uv run scripts/check_variant.py api --docker      # ... + image build and smoke test
    uv run scripts/check_variant.py all               # every variant

Requires uv, just, git and (for database variants and --docker) Docker.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from copier import run_copy

TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
VARIANTS: dict[str, dict[str, bool]] = {
    "api-db": {"has_web_api": True, "has_database": True},
    "api": {"has_web_api": True, "has_database": False},
    "db": {"has_web_api": False, "has_database": True},
    "minimal": {"has_web_api": False, "has_database": False},
}
READINESS_URL = "http://localhost:8000/health/ready"
READINESS_TIMEOUT_S = 90
NON_ROOT_USERS = {"", "root", "0"}


def run(*command: str, cwd: Path) -> str:
    print(f"$ {' '.join(command)}", flush=True)
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout


def render(variant: str, destination: Path) -> None:
    run_copy(
        str(TEMPLATE_ROOT),
        destination,
        data={
            "project_name": "Demo Service",
            "description": "A demo service.",
            **VARIANTS[variant],
        },
        vcs_ref="HEAD",
        defaults=True,
        quiet=True,
    )


def check_project(project: Path) -> None:
    run("git", "init", "--quiet", "--initial-branch", "main", cwd=project)
    run("uv", "lock", cwd=project)
    run("just", "setup", cwd=project)
    run("just", "check", cwd=project)
    run("git", "add", "--all", cwd=project)
    run("uv", "run", "pre-commit", "run", "--all-files", cwd=project)


def wait_until_ready() -> None:
    deadline = time.monotonic() + READINESS_TIMEOUT_S
    while True:
        try:
            with urllib.request.urlopen(READINESS_URL, timeout=2) as response:
                print(f"ready: {response.read().decode()}", flush=True)
                return
        except urllib.error.URLError, ConnectionError:
            if time.monotonic() > deadline:
                raise
            time.sleep(1)


def smoke_test_image(variant: str, project: Path) -> None:
    image = f"template-check-{variant}"
    run("docker", "build", "--quiet", "--tag", image, ".", cwd=project)
    user = run("docker", "image", "inspect", "--format", "{{.Config.User}}", image, cwd=project)
    if user.strip().split(":")[0] in NON_ROOT_USERS:
        raise SystemExit(f"{variant}: the image runs as root")

    options = VARIANTS[variant]
    if not options["has_web_api"]:
        run("docker", "run", "--rm", image, cwd=project)  # starts, logs and exits 0
    elif options["has_database"]:
        try:
            run("docker", "compose", "up", "--build", "--detach", "--wait", cwd=project)
            wait_until_ready()
            migrate = ("alembic", "upgrade", "head")
            run("docker", "compose", "run", "--rm", "app", *migrate, cwd=project)
        finally:
            run("docker", "compose", "down", "--volumes", cwd=project)
    else:
        container = run("docker", "run", "--detach", "--publish", "8000:8000", image, cwd=project)
        try:
            wait_until_ready()
        finally:
            run("docker", "rm", "--force", container.strip(), cwd=project)


def check_variant(variant: str, *, docker: bool, keep: bool) -> None:
    workdir = Path(tempfile.mkdtemp(prefix=f"template-{variant}-"))
    project = workdir / "demo-service"
    print(f"=== {variant}: {project}", flush=True)
    try:
        render(variant, project)
        check_project(project)
        if docker:
            smoke_test_image(variant, project)
    except subprocess.CalledProcessError as error:
        print(error.stdout, error.stderr, sep="\n", file=sys.stderr)
        raise SystemExit(f"{variant}: `{' '.join(error.cmd)}` failed") from error
    finally:
        if not keep:
            shutil.rmtree(workdir, ignore_errors=True)
    print(f"=== {variant}: ok", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render template variants and run their checks.")
    parser.add_argument("variant", choices=[*VARIANTS, "all"])
    parser.add_argument("--docker", action="store_true", help="also build and smoke-test the image")
    parser.add_argument("--keep", action="store_true", help="keep the generated project")
    args = parser.parse_args()

    variants = list(VARIANTS) if args.variant == "all" else [args.variant]
    for variant in variants:
        check_variant(variant, docker=args.docker, keep=args.keep)


if __name__ == "__main__":
    main()
