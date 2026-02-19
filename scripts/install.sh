#!/usr/bin/env bash
set -euo pipefail

# BuryatVPN auto-installer
# Usage examples:
#   ./scripts/install.sh
#   ./scripts/install.sh --with-dev
#   ./scripts/install.sh --system-packages --python python3.11

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="python3"
WITH_DEV=0
INSTALL_SYSTEM_PACKAGES=0
SKIP_ENV_TEMPLATE=0

log() { printf "[INFO] %s\n" "$*"; }
warn() { printf "[WARN] %s\n" "$*"; }
err() { printf "[ERR ] %s\n" "$*" >&2; }

usage() {
  cat <<EOF
BuryatVPN installer

Options:
  --with-dev            Install dev dependencies from requirements-dev.txt
  --system-packages     Install system packages via apt (Ubuntu/Debian)
  --python <bin>        Python binary to use (default: python3)
  --skip-env-template   Do not create .env from .env.example if .env missing
  -h, --help            Show this help
EOF
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Required command not found: $1"
    exit 1
  fi
}

install_system_packages() {
  if ! command -v apt-get >/dev/null 2>&1; then
    warn "apt-get not found; skip system packages installation"
    return
  fi

  log "Installing system packages (python3-venv, redis-server, build tools)..."
  sudo apt-get update
  sudo apt-get install -y python3-venv python3-pip redis-server build-essential libffi-dev libssl-dev
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --with-dev)
        WITH_DEV=1
        shift
        ;;
      --system-packages)
        INSTALL_SYSTEM_PACKAGES=1
        shift
        ;;
      --python)
        PYTHON_BIN="${2:-}"
        if [[ -z "${PYTHON_BIN}" ]]; then
          err "--python requires value"
          exit 1
        fi
        shift 2
        ;;
      --skip-env-template)
        SKIP_ENV_TEMPLATE=1
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        err "Unknown argument: $1"
        usage
        exit 1
        ;;
    esac
  done
}

main() {
  parse_args "$@"

  require_cmd "${PYTHON_BIN}"

  if [[ "${INSTALL_SYSTEM_PACKAGES}" -eq 1 ]]; then
    require_cmd sudo
    install_system_packages
  fi

  log "Using project root: ${ROOT_DIR}"
  cd "${ROOT_DIR}"

  if [[ ! -d "${VENV_DIR}" ]]; then
    log "Creating virtualenv: ${VENV_DIR}"
    "${PYTHON_BIN}" -m venv "${VENV_DIR}"
  else
    log "Virtualenv already exists: ${VENV_DIR}"
  fi

  # shellcheck source=/dev/null
  source "${VENV_DIR}/bin/activate"

  log "Upgrading pip/setuptools/wheel"
  pip install --upgrade pip setuptools wheel

  log "Installing runtime dependencies"
  pip install -r requirements.txt

  if [[ "${WITH_DEV}" -eq 1 ]]; then
    log "Installing development dependencies"
    pip install -r requirements-dev.txt
  fi

  if [[ ! -f .env && "${SKIP_ENV_TEMPLATE}" -eq 0 ]]; then
    log "Creating .env from template"
    cp .env.example .env
  fi

  mkdir -p data logs backups

  cat <<EOF

Installation completed ✅

Next steps:
1) Edit .env and fill required values:
   BOT_TOKEN, SECRET_KEY, ENCRYPTION_KEY, JWT_SECRET_KEY,
   WEB_ADMIN_EMAIL, WEB_ADMIN_PASSWORD_HASH
2) Activate env:
   source ${VENV_DIR}/bin/activate
3) Run app:
   python -m app.main
EOF
}

main "$@"
