#!/bin/bash
set -e

# Run the application with environment variables
python application.py \
    --username ${USERNAME:-Bob} \
    --discovery-port ${DISCOVERY_PORT:-5002} \
    --p2p-port ${P2P_PORT:-5003} \
    --db ${DB_URL:-postgresql://postgres:postgres@postgres:5432/postgres} 