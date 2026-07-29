#!/bin/sh
set -e

# Support cross-platform echo colors
BLUE="\033[34m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# Load environment variables if .env exists
if [ -f .env ]; then
  printf "${BLUE}Loading environment variables from .env...${RESET}\n"
  # Support Windows environment by stripping carriage returns before sourcing
  tr -d '\r' < .env > .env.tmp
  set -a
  . ./.env.tmp
  set +a
  rm -f .env.tmp
else
  printf "${YELLOW}Warning: .env file not found. Falling back to docker-compose defaults.${RESET}\n"
fi

printf "${BLUE}Starting ResearchOS infrastructure...${RESET}\n"

# Check for Docker Compose command availability
if command -v docker-compose >/dev/null 2>&1; then
  DC_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  DC_CMD="docker compose"
else
  printf "${RED}Error: docker-compose or docker compose is not installed or not in PATH.${RESET}\n"
  exit 1
fi

$DC_CMD up -d

printf "${BLUE}Waiting for database services to become healthy...${RESET}\n"

SERVICES="postgres redis qdrant neo4j"
MAX_ATTEMPTS=15
ATTEMPTS=0

# Define a function to check health status
check_health() {
  ALL_HEALTHY=1
  for service in $SERVICES; do
    CONTAINER_NAME="researchos-$service"
    
    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
      printf "Container ${YELLOW}$CONTAINER_NAME${RESET} not found yet.\n"
      ALL_HEALTHY=0
      continue
    fi
    
    # Extract health status
    STATUS=$(docker inspect --format='{{json .State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "\"none\"")
    STATUS=$(echo "$STATUS" | sed 's/"//g')
    
    if [ "$STATUS" != "healthy" ]; then
      printf "Service ${YELLOW}$service${RESET} is ${RED}$STATUS${RESET}\n"
      ALL_HEALTHY=0
    else
      printf "Service ${YELLOW}$service${RESET} is ${GREEN}healthy${RESET}\n"
    fi
  done
  
  if [ "$ALL_HEALTHY" -eq 1 ]; then
    return 0
  else
    return 1
  fi
}

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
  if check_health; then
    printf "\n${GREEN}All database services are up and healthy!${RESET}\n"
    printf "Qdrant Dashboard: http://localhost:6333/dashboard\n"
    printf "Neo4j Browser: http://localhost:7474\n"
    exit 0
  fi
  ATTEMPTS=$((ATTEMPTS+1))
  if [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; then
    printf "Retrying in 2 seconds... ($ATTEMPTS/$MAX_ATTEMPTS)\n\n"
    sleep 2
  fi
done

printf "${RED}Timeout reached. Some services failed to become healthy.\n${RESET}"
$DC_CMD ps
exit 1
