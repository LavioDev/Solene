#!/usr/bin/env bash
# ==============================================================================
# Solène Platform - Automated Production Deployment & Update Script
# ==============================================================================
set -e

PROJECT_DIR="/opt/solene"
WEBROOT_DIR="/opt/1panel/apps/openresty/openresty/www/sites/solene.io.vn/index"

cd "$PROJECT_DIR"

echo "====================================================="
echo "       SOLENE PLATFORM - UPDATE ASSISTANT            "
echo "====================================================="
echo "1) Update Everything (Frontend + Backend + Migration)"
echo "2) Update Frontend Only (UI, Vue, CSS)"
echo "3) Update Backend Only (FastAPI, Alembic Migration)"
echo "4) Check System Status & Health"
echo "5) Exit"
echo "====================================================="
read -rp "Please select an option [1-5]: " choice

update_frontend() {
    echo ""
    echo ">>> [1/2] Building Frontend using Docker node:20-alpine..."
    docker run --rm -v "$PROJECT_DIR/frontend:/app" -w /app node:20-alpine sh -c "npm install --legacy-peer-deps && npm run build"

    echo ">>> [2/2] Deploying assets to OpenResty webroot..."
    rm -rf "${WEBROOT_DIR:?}"/*
    cp -r "$PROJECT_DIR/frontend/dist"/* "$WEBROOT_DIR/"
    chmod -R 755 "$WEBROOT_DIR/"
    echo ">>> Frontend deployed successfully to https://solene.io.vn!"
}

update_backend() {
    echo ""
    echo ">>> [1/3] Building solene-backend Docker image..."
    cd "$PROJECT_DIR/backend"
    docker build -t solene-backend:latest .

    echo ">>> [2/3] Restarting solene-backend container..."
    docker rm -f solene-backend 2>/dev/null || true
    docker run -d \
      --name solene-backend \
      --restart unless-stopped \
      --net=host \
      -v "$PROJECT_DIR/uploads:/app/uploads" \
      solene-backend:latest

    echo ">>> [3/3] Running database migrations..."
    sleep 3
    docker exec solene-backend alembic upgrade head || true

    echo ">>> Backend deployed successfully!"
}

case $choice in
    1)
        echo ">>> Pulling latest changes from GitHub (origin/main)..."
        git pull origin main
        update_frontend
        update_backend
        echo ""
        echo "=== ALL UPDATES COMPLETED SUCCESSFULLY ==="
        ;;
    2)
        echo ">>> Pulling latest changes from GitHub (origin/main)..."
        git pull origin main
        update_frontend
        echo ""
        echo "=== FRONTEND UPDATE COMPLETED SUCCESSFULLY ==="
        ;;
    3)
        echo ">>> Pulling latest changes from GitHub (origin/main)..."
        git pull origin main
        update_backend
        echo ""
        echo "=== BACKEND UPDATE COMPLETED SUCCESSFULLY ==="
        ;;
    4)
        echo ""
        echo "=== DOCKER CONTAINERS ==="
        docker ps | grep solene || echo "No Solène containers running!"
        echo ""
        echo "=== BACKEND HEALTH CHECK ==="
        curl -s http://127.0.0.1:8200/health || echo "Backend unreachable!"
        echo ""
        echo "=== HTTPS LIVE STATUS ==="
        curl -sI https://solene.io.vn/ | head -n 5
        ;;
    5)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid selection."
        exit 1
        ;;
esac
