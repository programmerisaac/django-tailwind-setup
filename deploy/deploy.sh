#!/bin/bash

# deploy.sh
# Production deployment script for Onehux Web Service
# 
# Usage:
#   ./deploy.sh [OPTIONS]
#
# Options:
#   --first-time    First time deployment (installs system dependencies)
#   --update        Update deployment (code and dependencies only)
#   --restart       Restart services only
#   --help          Show this help message
#
# Author: Isaac

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="onehux-web-service"
PROJECT_USER="onehux"
PROJECT_PATH="/home/$PROJECT_USER/$PROJECT_NAME"
VENV_PATH="$PROJECT_PATH/venv"
REPO_URL="https://github.com/yourusername/$PROJECT_NAME.git"
BRANCH="main"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root!"
        print_error "Please run as the $PROJECT_USER user or with sudo for system tasks only."
        exit 1
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    sudo apt update
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        postgresql \
        postgresql-contrib \
        redis-server \
        nginx \
        git \
        curl \
        build-essential \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        nodejs \
        npm \
        supervisor \
        fail2ban \
        ufw \
        certbot \
        python3-certbot-nginx
    
    print_success "System dependencies installed!"
}

# Function to setup project user
setup_project_user() {
    print_status "Setting up project user..."
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        sudo useradd -m -s /bin/bash $PROJECT_USER
        sudo usermod -aG www-data $PROJECT_USER
        print_success "User $PROJECT_USER created!"
    else
        print_warning "User $PROJECT_USER already exists."
    fi
}

# Function to setup PostgreSQL
setup_postgresql() {
    print_status "Setting up PostgreSQL..."
    
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql -c "CREATE USER $PROJECT_USER WITH PASSWORD 'your_secure_password';" || true
    sudo -u postgres psql -c "CREATE DATABASE ${PROJECT_NAME//-/_}_prod OWNER $PROJECT_USER;" || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${PROJECT_NAME//-/_}_prod TO $PROJECT_USER;" || true
    
    print_success "PostgreSQL setup complete!"
}

# Function to setup Redis
setup_redis() {
    print_status "Setting up Redis..."
    
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # Configure Redis for production
    sudo sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
    sudo sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    
    sudo systemctl restart redis-server
    
    print_success "Redis setup complete!"
}

# Function to clone or update repository
setup_repository() {
    print_status "Setting up repository..."
    
    if [ ! -d "$PROJECT_PATH" ]; then
        print_status "Cloning repository..."
        git clone $REPO_URL $PROJECT_PATH
        cd $PROJECT_PATH
        git checkout $BRANCH
    else
        print_status "Updating repository..."
        cd $PROJECT_PATH
        git fetch origin
        git reset --hard origin/$BRANCH
    fi
    
    # Set proper permissions
    sudo chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_PATH
    
    print_success "Repository setup complete!"
}

# Function to setup Python virtual environment
setup_virtualenv() {
    print_status "Setting up Python virtual environment..."
    
    cd $PROJECT_PATH
    
    if [ ! -d "$VENV_PATH" ]; then
        python3 -m venv $VENV_PATH
    fi
    
    source $VENV_PATH/bin/activate
    pip install --upgrade pip
    pip install -r requirements/prod.txt
    
    print_success "Virtual environment setup complete!"
}

# Function to setup Node.js and Tailwind CSS
setup_nodejs() {
    print_status "Setting up Node.js and Tailwind CSS..."
    
    cd $PROJECT_PATH
    
    # Install Node.js dependencies
    npm install
    
    # Build CSS for production
    npm run prod
    
    print_success "Node.js and Tailwind CSS setup complete!"
}

# Function to setup environment files
setup_environment() {
    print_status "Setting up environment files..."
    
    cd $PROJECT_PATH
    
    if [ ! -f "prod.env" ]; then
        print_warning "prod.env file not found! Creating template..."
        cp prod.env.example prod.env 2>/dev/null || true
        print_error "Please edit prod.env with your production settings!"
        return 1
    fi
    
    # Set proper permissions for environment files
    chmod 600 prod.env
    chmod 600 dev.env 2>/dev/null || true
    
    print_success "Environment files setup complete!"
}

# Function to run Django management commands
run_django_commands() {
    print_status "Running Django management commands..."
    
    cd $PROJECT_PATH
    source $VENV_PATH/bin/activate
    
    export DJANGO_ENV=production
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Run migrations
    python manage.py migrate
    
    # Create superuser (only if it doesn't exist)
    echo "Creating superuser (if needed)..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@onehuxwebservice.com', 'admin_password_change_me')
    print('Superuser created!')
else:
    print('Superuser already exists.')
" || true
    
    print_success "Django commands completed!"
}

# Function to setup systemd services
setup_systemd_services() {
    print_status "Setting up systemd services..."
    
    # Copy service files
    sudo cp deployment/systemd/onehux-web.service /etc/systemd/system/
    sudo cp deployment/systemd/onehux-web.socket /etc/systemd/system/
    sudo cp deployment/systemd/onehux-celery.service /etc/systemd/system/
    sudo cp deployment/systemd/onehux-celery-beat.service /etc/systemd/system/
    
    # Update service files with correct paths
    sudo sed -i "s|/home/onehux/onehux-web-service|$PROJECT_PATH|g" /etc/systemd/system/onehux-*.service
    sudo sed -i "s|User=onehux|User=$PROJECT_USER|g" /etc/systemd/system/onehux-*.service
    sudo sed -i "s|Group=onehux|Group=$PROJECT_USER|g" /etc/systemd/system/onehux-*.service
    
    # Create necessary directories
    sudo mkdir -p /var/log/celery
    sudo mkdir -p /var/run/celery
    sudo chown $PROJECT_USER:$PROJECT_USER /var/log/celery
    sudo chown $PROJECT_USER:$PROJECT_USER /var/run/celery
    
    # Reload systemd and enable services
    sudo systemctl daemon-reload
    sudo systemctl enable onehux-web.socket
    sudo systemctl enable onehux-web.service
    sudo systemctl enable onehux-celery.service
    sudo systemctl enable onehux-celery-beat.service
    
    print_success "Systemd services setup complete!"
}

# Function to setup Nginx
setup_nginx() {
    print_status "Setting up Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/$PROJECT_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name onehuxwebservice.com www.onehuxwebservice.com;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name onehuxwebservice.com www.onehuxwebservice.com;
    
    # SSL Configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/onehuxwebservice.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/onehuxwebservice.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Static files
    location /static/ {
        alias $PROJECT_PATH/static/;
        expires 1M;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias $PROJECT_PATH/media/;
        expires 1M;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/onehux-web.sock;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$http_host;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security
    location ~ /\. {
        deny all;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and restart Nginx
    sudo nginx -t
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    print_success "Nginx setup complete!"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    sudo systemctl start onehux-web.socket
    sudo systemctl start onehux-web.service
    sudo systemctl start onehux-celery.service
    sudo systemctl start onehux-celery-beat.service
    
    print_success "Services started!"
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    
    sudo systemctl restart onehux-web.service
    sudo systemctl restart onehux-celery.service
    sudo systemctl restart onehux-celery-beat.service
    sudo systemctl reload nginx
    
    print_success "Services restarted!"
}

# Function to show status
show_status() {
    print_status "Service Status:"
    echo "===================="
    
    services=("onehux-web" "onehux-celery" "onehux-celery-beat" "nginx" "postgresql" "redis-server")
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet $service; then
            echo -e "$service: ${GREEN}RUNNING${NC}"
        else
            echo -e "$service: ${RED}STOPPED${NC}"
        fi
    done
    
    echo ""
    print_status "Checking application..."
    curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/ || echo "Application not responding"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall..."
    
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    
    print_success "Firewall setup complete!"
}

# Function to show help
show_help() {
    echo "Onehux Web Service Deployment Script"
    echo "===================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --first-time    First time deployment (installs everything)"
    echo "  --update        Update deployment (code and dependencies only)"
    echo "  --restart       Restart services only"
    echo "  --status        Show service status"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --first-time    # First deployment"
    echo "  $0 --update        # Update existing deployment"
    echo "  $0 --restart       # Restart services after config changes"
    echo ""
}

# Main execution
main() {
    case "${1:-}" in
        --first-time)
            print_status "Starting first-time deployment..."
            check_root
            install_system_dependencies
            setup_project_user
            setup_postgresql
            setup_redis
            setup_repository
            setup_virtualenv
            setup_nodejs
            setup_environment
            run_django_commands
            setup_systemd_services
            setup_nginx
            setup_firewall
            start_services
            show_status
            print_success "First-time deployment complete!"
            print_warning "Don't forget to:"
            print_warning "1. Edit prod.env with your settings"
            print_warning "2. Set up SSL with: sudo certbot --nginx"
            print_warning "3. Change the default superuser password"
            ;;
        --update)
            print_status "Starting update deployment..."
            setup_repository
            setup_virtualenv
            setup_nodejs
            run_django_commands
            restart_services
            show_status
            print_success "Update deployment complete!"
            ;;
        --restart)
            print_status "Restarting services..."
            restart_services
            show_status
            print_success "Services restarted!"
            ;;
        --status)
            show_status
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Invalid option: ${1:-}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
