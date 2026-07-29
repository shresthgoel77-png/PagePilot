#!/bin/sh
set -e

BLUE="\033[34m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

printf "${BLUE}Stopping ResearchOS infrastructure...${RESET}\n"

if command -v docker-compose >/dev/null 2>&1; then
  DC_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  DC_CMD="docker compose"
else
  printf "${RED}Error: docker-compose or docker compose is not installed or not in PATH.${RESET}\n"
  exit 1
fi

if [ "$1" = "--volumes" ]; then
  printf "${YELLOW}Warning: Removing persistent volumes...${RESET}\n"
  $DC_CMD down --volumes
else
  $DC_CMD down
fi

printf "${GREEN}Infrastructure stopped gracefully.${RESET}\n"
