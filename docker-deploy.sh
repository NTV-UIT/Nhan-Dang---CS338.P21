#!/bin/bash

# Docker build and deployment script for StyleCLIP project

set -e

echo "🐳 StyleCLIP Docker Build & Deploy Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed."
}

# Check NVIDIA Docker support
check_nvidia_docker() {
    if command -v nvidia-docker &> /dev/null || docker info | grep -q nvidia; then
        print_success "NVIDIA Docker support detected."
        return 0
    else
        print_warning "NVIDIA Docker support not detected. GPU acceleration may not work."
        return 1
    fi
}

# Download pretrained models if not exist
setup_pretrained_models() {
    print_status "Checking pretrained models..."
    
    if [ ! -d "backend/pretrained_models" ] || [ -z "$(ls -A backend/pretrained_models)" ]; then
        print_status "Downloading pretrained models..."
        cd backend
        mkdir -p pretrained_models
        if [ -f "down_ckp.sh" ]; then
            chmod +x down_ckp.sh
            ./down_ckp.sh
        else
            print_warning "down_ckp.sh not found. Please download pretrained models manually."
        fi
        cd ..
    else
        print_success "Pretrained models already exist."
    fi
}

# Build images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend
    print_status "Building backend image..."
    docker build -f backend/Dockerfile -t styleclip-backend:latest .
    
    # Build frontend
    print_status "Building frontend image..."
    docker build -f frontend/Dockerfile -t styleclip-frontend:latest .
    
    print_success "All images built successfully."
}

# Deploy with docker-compose
deploy() {
    print_status "Deploying with Docker Compose..."
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Start services
    if check_nvidia_docker; then
        print_status "Starting with GPU support..."
        docker-compose up -d
    else
        print_warning "Starting without GPU support..."
        # Remove GPU requirements from docker-compose temporarily
        sed 's/deploy:/# deploy:/' docker-compose.yml > docker-compose.nogpu.yml
        sed 's/resources:/# resources:/' docker-compose.nogpu.yml > temp.yml && mv temp.yml docker-compose.nogpu.yml
        sed 's/reservations:/# reservations:/' docker-compose.nogpu.yml > temp.yml && mv temp.yml docker-compose.nogpu.yml
        sed 's/devices:/# devices:/' docker-compose.nogpu.yml > temp.yml && mv temp.yml docker-compose.nogpu.yml
        sed 's/- driver: nvidia/# - driver: nvidia/' docker-compose.nogpu.yml > temp.yml && mv temp.yml docker-compose.nogpu.yml
        sed 's/count: 1/# count: 1/' docker-compose.nogpu.yml > temp.yml && mv temp.yml docker-compose.nogpu.yml
        sed 's/capabilities: \[gpu\]/# capabilities: [gpu]/' docker-compose.nogpu.yml > temp.yml && mv temp.yml docker-compose.nogpu.yml
        
        docker-compose -f docker-compose.nogpu.yml up -d
        rm docker-compose.nogpu.yml
    fi
    
    print_success "Services started successfully."
}

# Show status
show_status() {
    print_status "Checking service status..."
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Nginx Proxy: http://localhost:80"
    
    echo ""
    print_status "To view logs:"
    echo "  docker-compose logs -f [service_name]"
    
    echo ""
    print_status "To stop services:"
    echo "  docker-compose down"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "check")
            check_docker
            check_nvidia_docker
            ;;
        "setup")
            check_docker
            setup_pretrained_models
            ;;
        "build")
            check_docker
            setup_pretrained_models
            build_images
            ;;
        "deploy")
            check_docker
            setup_pretrained_models
            build_images
            deploy
            show_status
            ;;
        "start")
            docker-compose up -d
            show_status
            ;;
        "stop")
            docker-compose down
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "clean")
            print_status "Cleaning up..."
            docker-compose down
            docker system prune -f
            print_success "Cleanup completed."
            ;;
        *)
            echo "Usage: $0 {check|setup|build|deploy|start|stop|status|logs|clean}"
            echo ""
            echo "Commands:"
            echo "  check   - Check Docker installation and requirements"
            echo "  setup   - Download pretrained models"
            echo "  build   - Build Docker images"
            echo "  deploy  - Full deployment (setup + build + start)"
            echo "  start   - Start services"
            echo "  stop    - Stop services"
            echo "  status  - Show service status"
            echo "  logs    - Show service logs"
            echo "  clean   - Clean up containers and images"
            exit 1
            ;;
    esac
}

main "$@"
