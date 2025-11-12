#!/bin/bash

# Travel Marketplace Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="travel_marketplace"
BACKUP_DIR="/var/backups"
LOG_FILE="/var/log/deploy.log"
HEALTH_CHECK_URL="http://localhost:8000/health/"
MAX_DEPLOYMENT_TIME=300  # 5 minutes

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
    echo -e "$1"
}

# Error handling
error_exit() {
    log "${RED}ERROR: $1${NC}"
    exit 1
}

# Success message
success() {
    log "${GREEN}SUCCESS: $1${NC}"
}

# Warning message
warning() {
    log "${YELLOW}WARNING: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error_exit "Please run this script as a non-root user"
    fi
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    BACKUP_NAME="${PROJECT_NAME}_$(date +%Y%m%d_%H%M%S)"
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
    
    mkdir -p $BACKUP_PATH
    
    # Backup database
    pg_dump $DATABASE_URL > "${BACKUP_PATH}/database.sql"
    
    # Backup media files
    if [ -d "/app/media" ]; then
        cp -r /app/media "${BACKUP_PATH}/"
    fi
    
    # Backup static files
    if [ -d "/app/staticfiles" ]; then
        cp -r /app/staticfiles "${BACKUP_PATH}/"
    fi
    
    # Create compressed backup
    tar -czf "${BACKUP_PATH}.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
    rm -rf "$BACKUP_PATH"
    
    success "Backup created: ${BACKUP_PATH}.tar.gz"
}

# Update dependencies
update_dependencies() {
    log "Updating dependencies..."
    
    # Update pip packages
    pip install -r requirements.txt
    
    # Update npm packages if frontend exists
    if [ -f "package.json" ]; then
        npm install
        npm run build
    fi
    
    success "Dependencies updated"
}

# Database migrations
run_migrations() {
    log "Running database migrations..."
    
    python manage.py migrate --noinput
    
    success "Migrations completed"
}

# Collect static files
collect_static() {
    log "Collecting static files..."
    
    python manage.py collectstatic --noinput --clear
    
    success "Static files collected"
}

# Create superuser if needed
create_superuser() {
    log "Checking for superuser..."
    
    if ! python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('CREATE_SUPERUSER')
" | grep -q 'CREATE_SUPERUSER'; then
        log "Creating superuser..."
        python manage.py createsuperuser --noinput \
            --username admin \
            --email admin@travelmarketplace.com \
            --first_name Admin \
            --last_name User || true
        success "Superuser created"
    else
        log "Superuser already exists"
    fi
}

# Health check
health_check() {
    log "Performing health check..."
    
    local start_time=$(date +%s)
    local timeout=$MAX_DEPLOYMENT_TIME
    
    while [ $(($(date +%s) - start_time)) -lt $timeout ]; do
        if curl -f -s "$HEALTH_CHECK_URL" > /dev/null; then
            success "Health check passed"
            return 0
        fi
        sleep 5
    done
    
    error_exit "Health check failed after $timeout seconds"
}

# Restart services
restart_services() {
    log "Restarting services..."
    
    # Restart Gunicorn
    systemctl restart gunicorn || supervisorctl restart gunicorn
    
    # Restart Nginx
    systemctl restart nginx
    
    # Restart Celery
    systemctl restart celery || supervisorctl restart celery
    systemctl restart celery-beat || supervisorctl restart celery-beat
    
    success "Services restarted"
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups (retention: $BACKUP_RETENTION_DAYS days)..."
    
    find $BACKUP_DIR -name "${PROJECT_NAME}_*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
    
    success "Old backups cleaned up"
}

# Rollback function
rollback() {
    log "Initiating rollback..."
    
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/${PROJECT_NAME}_*.tar.gz | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        error_exit "No backup found for rollback"
    fi
    
    # Extract backup
    tar -xzf "$LATEST_BACKUP" -C "$BACKUP_DIR"
    BACKUP_DIR_NAME=$(basename "$LATEST_BACKUP" .tar.gz)
    EXTRACTED_PATH="${BACKUP_DIR}/${BACKUP_DIR_NAME}"
    
    # Restore database
    psql $DATABASE_URL < "${EXTRACTED_PATH}/database.sql"
    
    # Restore files
    if [ -d "${EXTRACTED_PATH}/media" ]; then
        rm -rf /app/media
        mv "${EXTRACTED_PATH}/media" /app/
    fi
    
    if [ -d "${EXTRACTED_PATH}/staticfiles" ]; then
        rm -rf /app/staticfiles
        mv "${EXTRACTED_PATH}/staticfiles" /app/
    fi
    
    # Cleanup
    rm -rf "$EXTRACTED_PATH"
    
    restart_services
    health_check
    
    success "Rollback completed"
}

# Main deployment function
deploy() {
    log "Starting deployment process..."
    
    check_root
    backup_current
    update_dependencies
    run_migrations
    collect_static
    create_superuser
    restart_services
    cleanup_backups
    
    # Wait for services to start
    sleep 10
    
    health_check
    
    success "Deployment completed successfully!"
}

# Show usage
usage() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  deploy    - Deploy the application"
    echo "  rollback  - Rollback to the previous backup"
    echo "  backup    - Create a backup without deploying"
    echo "  health     - Perform health check"
    echo "  logs       - Show deployment logs"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 rollback"
    echo "  $0 backup"
}

# Show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        error_exit "Log file not found: $LOG_FILE"
    fi
}

# Parse command line arguments
case "$1" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    backup)
        backup_current
        ;;
    health)
        health_check
        ;;
    logs)
        show_logs
        ;;
    *)
        usage
        exit 1
        ;;
esac