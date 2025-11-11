#!/usr/bin/env bash

set -euo pipefail

CONTAINER_NAME="${CONTAINER_NAME:-webapp-redis}"
IMAGE="${REDIS_IMAGE:-redis:7-alpine}"
PORT="${REDIS_PORT:-6379}"

usage() {
  cat <<EOF
Usage: $(basename "$0") <command>

Commands:
  start   Start Redis in Docker (creates container if needed)
  stop    Stop the Redis container
  status  Show container status
  logs    Tail Redis logs (Ctrl+C to exit)

Environment variables:
  CONTAINER_NAME  Name of the Redis container (default: webapp-redis)
  REDIS_IMAGE     Docker image to use (default: redis:7-alpine)
  REDIS_PORT      Host port to bind (default: 6379)
EOF
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker command not found. Please install Docker first." >&2
    exit 1
  fi
}

container_exists() {
  docker ps -a --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "${CONTAINER_NAME}"
}

start() {
  ensure_docker

  if container_running; then
    echo "Redis container '${CONTAINER_NAME}' is already running."
    return
  fi

  if container_exists; then
    docker start "${CONTAINER_NAME}" >/dev/null
    echo "Redis container '${CONTAINER_NAME}' started on port ${PORT}."
  else
    docker run -d \
      --name "${CONTAINER_NAME}" \
      -p "${PORT}:6379" \
      --restart unless-stopped \
      "${IMAGE}" >/dev/null
    echo "Redis container '${CONTAINER_NAME}' created and started on port ${PORT}."
  fi
}

stop() {
  ensure_docker

  if container_running; then
    docker stop "${CONTAINER_NAME}" >/dev/null
    echo "Redis container '${CONTAINER_NAME}' stopped."
  else
    echo "Redis container '${CONTAINER_NAME}' is not running."
  fi
}

status() {
  ensure_docker

  if container_running; then
    echo "Redis container '${CONTAINER_NAME}' is running."
  elif container_exists; then
    echo "Redis container '${CONTAINER_NAME}' exists but is stopped."
  else
    echo "Redis container '${CONTAINER_NAME}' has not been created."
  fi
}

logs() {
  ensure_docker

  if container_exists; then
    docker logs -f "${CONTAINER_NAME}"
  else
    echo "Redis container '${CONTAINER_NAME}' has not been created." >&2
    exit 1
  fi
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

case "$1" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  logs) logs ;;
  *) usage; exit 1 ;;
esac

