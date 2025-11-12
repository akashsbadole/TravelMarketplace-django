# Travel Marketplace

This is a comprehensive multi-vendor travel marketplace application built with Django, enabling customers to submit travel requirements, agents to provide quotes, and bookings to be made seamlessly through the platform. The platform generates commission from both agents (2%) and customers (1%) on successful transactions.

## Screenshot

![Home-TravelMarketplace](Home-TravelMarketplace.png "Home TravelMarketplace")
![Home-TravelMarketplace](TravelMarketplace-Destinations-Travel-Marketplace.png "Home TravelMarketplace")
![Home-TravelMarketplace](TravelMarketplace-Travel-Agents-Travel-Marketplace.png "Home TravelMarketplace")

## Features

The Travel Marketplace offers a rich set of features for various user roles:

### Core Functionality

- **User Authentication**: Secure user registration, login, and profile management.
- **Role-Based Access**: Distinct dashboards and functionalities for customers, agents, and administrators.
- **Commission System**: Automated calculation and management of commissions from agents and customers.

### Customer Features

- **Requirement Submission**: Customers can submit detailed travel requirements, with dynamic forms adapting to different service types (flights, hotels, etc.). Includes support for file uploads.
- **User Dashboard**: A personalized dashboard for customers to:
  - View real-time statistics and analytics.
  - Manage submitted requirements, including tracking status, editing, and archiving.
  - Track and manage all bookings.
  - Compare multiple quotes side-by-side from various agents.
  - Receive and manage system notifications.
- **Flight & Hotel Search**: Integration with Amadeus API for comprehensive flight and hotel search capabilities.
- **Flight Inspiration**: Discover travel destinations based on budget and origin.
- **Search History**: Keep track of past flight and hotel searches.

### Agent Features

- **Agent Dashboard**: A dedicated dashboard for agents to:
  - View earnings and performance metrics (real data, replacing previous mock data).
  - Browse and respond to customer travel requirements.
  - Create and manage detailed travel quotes with a rich text editor and templates.
  - Manage bookings handled by the agent.
  - Request payouts for earned commissions.
- **Quote Builder**: Enhanced tool to build quotes using real-time Amadeus flight and hotel data.

### Administrator Features

- **Admin Panel**: A centralized administrative interface for:
  - Comprehensive system overview with key metrics and analytics.
  - User and agent management, including verification workflows.
  - Booking and payment tracking.
  - Dispute resolution system.
  - System settings management, including commission rates.

### Technical & Platform Features

- **RESTful API**: Built with Django REST Framework for flexible data interaction.
- **CORS Support**: Configured for cross-origin resource sharing.
- **Media Management**: Dedicated handling for uploaded media files.
- **Email Services**: Configurable email backend for notifications and communication.
- **API Keys Management**: Centralized management for Amadeus and other third-party API keys (to be moved to .env in production).
- **Logging**: Detailed application logging for monitoring and debugging.
- **Caching**: Implemented for API search results to reduce redundant calls and improve performance.

## Deployment

This section provides a high-level overview of the deployment process. For detailed instructions, please refer to the `DEPLOYMENT.md` file in the `deploy/` directory.

### Prerequisites

- **Operating System**: Ubuntu 20.04+ or CentOS 8+
- **Python**: 3.9+
- **Node.js**: 16+ (for frontend build tools)
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Nginx**: 1.18+
- **SSL Certificate**: For production HTTPS

### Environment Setup

1.  **Project Directory**: Create `/opt/travel_marketplace`.
2.  **Clone Repository**: `git clone https://github.com/your-org/travel-marketplace.git .`
3.  **Python Environment**: `python3.9 -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`.
4.  **Environment Variables**: Copy `deploy/.env.example` to `.env` and configure `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `ALLOWED_HOSTS`.

### Database Configuration

- **PostgreSQL**: Set up user and database (e.g., `travel_marketplace`).
- **Migrations**: `python manage.py migrate`.

### Application Configuration

- **Static Files**: `python manage.py collectstatic --noinput`, configure permissions.
- **Celery**: Set up Celery user and directories.
- **SSL Certificate**: Configure Nginx for SSL (Certbot recommended).

### Deployment Methods

#### 1. Docker Deployment (Recommended)

- Build Docker Image: `docker build -t travel-marketplace:latest .`
- Deploy with Docker Compose: `docker-compose -f deploy/docker-compose.yml up -d`
- Services include: `web` (Django/Gunicorn), `db` (PostgreSQL), `redis`, `celery`, `celery-beat`, `nginx`.

#### 2. Manual Deployment

- **Systemd Services**: Create and configure `systemd` services for Gunicorn (`travel-marketplace.service`) and Celery (`celery.service`).
- **Nginx Configuration**: Copy and enable `deploy/nginx/nginx.conf`, test, and reload Nginx.
- **Start Services**: `sudo systemctl daemon-reload`, `sudo systemctl enable/start travel-marketplace celery nginx`.

### Testing

The project includes automated tests (unit, integration, load, security) that can be run using `python manage.py test`. Refer to `DEPLOYMENT.md` for specific commands and security tools.

### Monitoring

- **Application Monitoring**: Health checks (`/health/`), detailed logging (e.g., `/var/log/django/travel_marketplace.log`).
- **Performance Monitoring**: APM integration (Sentry, New Relic, Datadog), database slow query logging.
- **Infrastructure Monitoring**: Prometheus and Grafana for system-level metrics.

### Security

- **Firewall**: Configure UFW to allow necessary ports (SSH, HTTP, HTTPS).
- **Security Headers**: Application includes HSTS, X-Frame-Options, X-Content-Type-Options, CSP.
- **SSL Configuration**: Regular SSL certificate testing and renewal.
- **Regular Updates**: Automated system and Python package updates, security scans with Bandit and Safety.

---

**Note**: This `README.md` provides an overview. For detailed step-by-step instructions on deployment and other configurations, please consult `DEPLOYMENT.md`, `implementation_plan.md`, and other relevant documentation files.
