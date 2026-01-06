# Budget-Tracker-COM3033
## Project Overview

This project is a budget tracking web application. The application allows 
users to manage their personal finances by recording transactions, categorising spending, tracking points, and 
receiving alerts based on their activity.
The system is designed using a microservice architecture, where each core domain of the application is implemented as 
an independent service. This approach improves modularity, scalability, and maintainability.
The application includes a Flask-based web user interface that communicates with multiple backend services via HTTP APIs. 
Each service focuses on a specific area of the system’s functionality, such as authentication, transactions, analytics, 
alerts, or points management.
---

## Key Features

The Budget Tracker application provides the following functionality:

- User registration and authentication  
- Transaction creation and management  
- Category and Budget management for expenses  
- Aggregated analytics and summaries  
- Alerts based on spending behaviour  
- A points system

All features are implemented using loosely coupled services that communicate over RESTful APIs.

---

## System Architecture

The system is composed of a web frontend and multiple backend microservices, each running independently. The services 
are containerised and can be orchestrated together using Docker Compose.

### Frontend

- **Web Application (Flask)**  
  Acts as the main user interface. It renders HTML templates and communicates with backend services to fetch and submit data.

### Backend Services

- **Auth Service (Flask)**  
  Handles user registration, authentication, and user data management.

- **Transaction Service (FastAPI)**  
  Manages transactions and exposes endpoints for transaction-related data and analytics queries.

- **Category Service (Flask)**  
  Handles CRUD operations for transaction categories and category wise budgets.

- **Analytics Service (Flask)**  
  Aggregates and processes data retrieved from the Transaction Service to provide higher level insights.

- **Alerts Service (Flask)**  
  Manages alerts and notifications and includes a background job for periodic alert processing.

- **Points Service (Flask)**  
  Implements a points system, including a background job for scheduled updates.

---

## Services and Ports

Each service runs on a dedicated port:

| Service | Port |
|------|------|
| Web Application | 5000 |
| Auth Service | 5001 |
| Transaction Service | 5002 |
| Category Service | 5003 |
| Analytics Service | 5004 |
| Alerts Service | 5005 |
| Points Service | 5006 |

---

## Technologies Used

- Python 3  
- Flask (Web App, Auth, Category, Analytics, Alerts, Points)  
- FastAPI (Transaction Service)  
- SQLAlchemy (ORM)   
- Docker and Docker Compose  
- Gunicorn and Uvicorn  

---

## Running the Project

The project can be run either using Docker Compose or directly using Python for local development.

---

## Option 1: Running with Docker Compose 

Docker Compose automatically builds and runs all services together in a consistent environment.

### Steps

1. Ensure Docker and Docker Compose are installed.
2. Navigate to the project root directory.
3. Run the following command:

```bash
docker-compose up --build
```
4. Once all services are running, open the application in a browser.
5. To stop the application, use:

```bash
docker-compose down
```
## Option 2: Running Locally with Python

This option is useful for development or debugging without containers.

### Steps

1. Create and activate a virtual environment: 
```bash
python -m venv .venv
```
Windows: 
```bash
.venv\Scripts\activate
```
MacOS: 
```bash
source .venv/bin/activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. Start all services using the provided helper script:
```bash
python run_all.py
```
