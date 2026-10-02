# Uniform commands (HANDBOOK §3) for the template itself. Requires uv, Docker and Node.js (npx).

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

prettier := "npx --yes prettier@3.9.9"
markdownlint := "npx --yes markdownlint-cli2@0.23.3"
ruff := "uvx ruff@0.16.10"
actionlint := "rhysd/actionlint:1.7.12@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667"

# List the recipes
default:
    @just --list

# Lint workflows, the check script and the docs
lint:
    docker run --rm -v "{{ justfile_directory() }}:/repo" -w /repo {{ actionlint }}
    {{ ruff }} check scripts
    {{ ruff }} format --check scripts
    {{ prettier }} --check .
    {{ markdownlint }}

# Render variants and run their own checks: just test api-db --docker (api-db, api, db, minimal, all)
test variant="all" *flags:
    uv run scripts/check_variant.py {{ variant }} {{ flags }}

# Everything CI checks
check: lint (test "all" "--docker")

# Format the script and the docs
fmt:
    {{ ruff }} format scripts
    {{ prettier }} --write .
