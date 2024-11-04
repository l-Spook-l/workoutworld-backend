# FastAPI React WorkoutWorld website server

![FastAPI](https://img.shields.io/badge/FastAPI-Web_Framework-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?logo=python)
![smtplib](https://img.shields.io/badge/smtplib-Email-orange)
![Pydantic](https://img.shields.io/badge/Pydantic-Data_Validation-green)
![RestAPI](https://img.shields.io/badge/RestAPI-Development-yellow)
![NGINX](https://img.shields.io/badge/NGINX-Web_Server-green?logo=nginx)
![Docker](https://img.shields.io/badge/Docker-Containerization-blue?logo=docker)
![Celery](https://img.shields.io/badge/Celery-Task_Queue-blue?logo=celery)
![Redis](https://img.shields.io/badge/Redis-Cache-red?logo=redis)
![Grafana](https://img.shields.io/badge/Grafana-Monitoring-green?logo=grafana)

# Project Description

The Fitness Web Platform is an online service that offers a wide range of workouts and enables users to create and track their individual training programs.

This project aims to provide a convenient and flexible platform for everyone striving for an active lifestyle and caring about their health.

## Server-Side Description

This repository contains the server-side part of the project built on FastAPI. In this project, the server provides an API for the client-side, allowing for creating, retrieving, and handling user workout data.

## Functionality

- Handling requests from the client-side (React) through an API.
- Working with a PostgreSQL database using SQLAlchemy ORM.
- Supporting CRUD operations for workout data.


## Update - October 2024

### New Features and Improvements

- **Admin Panel**: Implemented a full-featured admin panel for easier management of settings, permissions, and data monitoring.
- **Celery Integration**: Added Celery for asynchronous task management, improving performance and user experience.
- **Grafana Support**: Integrated Grafana for enhanced data visualization and real-time monitoring through customizable dashboards.
- **Code Structure**: Refactored the codebase for improved maintainability and readability.
- **Automated Tests**: Introduced a suite of tests to ensure stability and catch potential issues early in development.


## Installation Requirements

- Python 3.12
- Dependencies from the requirements.txt file

## Usage

**Running the Application:**
   - Navigate to the project's root directory and execute this command in the terminal to start the application.
   
     ```bash
     uvicorn src.main:app --reload
     ```

## Planned Changes

Planned development for the project includes:

- **Forum:** Adding a forum feature for discussing workouts, exchanging experiences, and sharing advice.
- **Sporting Goods Store:** Creating a section for sports goods where users can purchase necessary equipment and accessories.
- **Group Workout Organization:** Implementing a feature for organizing group sessions with the ability to sign up and manage the workout schedule.

## Developers

- https://github.com/l-Spook-l

## Contact

If you have any questions or suggestions for improving the project, please contact uaspookua@gmail.com.
