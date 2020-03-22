## FECH

### Pre-Requisites

Docker, Docker-Compose

#### Install Docker

https://get.docker.com/

    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    
Make sure to give the current user to docker group after installation:

    sudo usermod -aG docker $USER
    
Before using docker, the terminal or SHH connection should be reopened.
    
#### Install DockerCompose 

https://docs.docker.com/compose/install/

### Installation Localhost/Development (For Ubuntu)

#### Run backend

Create the .env file:

    cp .env.example .env
    
Update env file with the desired values.
    
Build with docker:

    docker-compose up -d --build backend_dev
    
Backend should be running on http://localhost:8000.

### Installation Production (For Ubuntu)
    
#### Run backend

Create the .env file:

    cp .env.example .env
    
Update env file with the desired values.

Build with docker:

    docker-compose up -d --build backend

Backend should be running on http://localhost:8000.

### Create first admin

    docker-compose exec backend python manage.py createsuperuser
    