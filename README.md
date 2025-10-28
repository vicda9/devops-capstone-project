# DevOps Capstone Template

![Build Status](https://github.com/vicda9/devops-capstone-project/actions/workflows/ci-build.yaml/badge.svg)


[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-green.svg)](https://shields.io/)

Customer Accounts Microservice
Overview

A RESTful Python service for managing customer accounts, built with Flask and SQLAlchemy. It exposes CRUD operations (create, read, update, delete, list) over HTTP and persists data to a relational database.


Technology Stack:

Flask for the web framework

SQLAlchemy for ORM and data modeling

Nose for unit testing with a 95% coverage threshold

Flake8 for linting and code quality enforcement

Flask-Talisman and Flask-CORS for security headers and CORS support

Docker and OpenShift/Kubernetes for containerization and deployment

Tekton pipeline for automated CI/CD


Chronological Enhancements and Revisions

1. Initial Service Implementation and TDD

    Test cases for CRUD operations were defined under tests/, covering models, routes, and CLI commands.

    The Account model (fields: id, name, email, address, phone_number, date_joined) was implemented in service/models.py.

    REST API endpoints were implemented in service/routes.py to satisfy each test.

2. Command-Line Interface

    db-create and other Flask CLI commands were added in service/common/cli_commands.py to automate database setup.

3. Code Quality and Security

    Flake8 configuration was added to enforce style, complexity, and line-length limits.
 
    A GitHub Actions workflow (CI) was configured to run linting and unit tests on every push and pull request.

    Security headers and CORS policies were integrated by revising service/config.py and initializing Flask-Talisman and Flask-CORS in service/routes.py.

4. Containerization

    A Dockerfile was authored to build a container image named “accounts,” based on python:3.9-slim, installing dependencies, and configuring gunicorn.

5. Database Service on OpenShift

    A PostgreSQL instance was provisioned in OpenShift, with secrets created for database credentials.

    Environment variables for DATABASE_HOST, DATABASE_NAME, DATABASE_USER, and DATABASE_PASSWORD were mapped from those secrets.

5. Kubernetes/OpenShift Manifests

    Deployment and Service YAML manifests were placed in deploy/deployment.yaml and deploy/service.yaml, using the image registry and wiring secrets.

    A PersistentVolumeClaim was defined in pvc.yaml to support workspace persistence during pipeline runs.

7. Automated CI/CD with Tekton

    A CD pipeline definition was added in pipeline.yaml, orchestrating tasks for cleanup, git-clone, lint (flake8), tests (nose), image build (buildah), and deploy (openshift-client).

    Custom Task definitions for echo, cleanup, and nose were created in tasks.yaml to support pipeline steps.

    The deploy step applies the manifests in deploy/ and verifies pod creation via oc get pods -l app=accounts.


Key Contributions:

service/models.py – Definition of the Account data model, including fields for id, name, email, address, phone_number, and date_joined, along with persistence logic.
service/routes.py – Implementation of REST API endpoints to handle account creation, retrieval, update, deletion, and listing.
service/config.py – Central Flask configuration, integration of Flask-Talisman for security headers and Flask-CORS for cross-origin policies.
service/common/log_handlers.py & error_handlers.py – Consolidated logging setup and uniform error responses across the microservice.
service/common/cli_commands.py – Custom Flask CLI commands enabling database initialization and management tasks via the command line.
tests/ – Comprehensive unit tests for models, routes, and CLI commands (68 tests, >94% coverage), ensuring reliability and adherence to TDD practices.
Dockerfile – Construction of a lightweight Python container image, installing only required runtime dependencies.
deploy/deployment.yaml & deploy/service.yaml – Kubernetes/OpenShift manifest files defining Deployment (3 replicas) and Service (ClusterIP on port 8080) for the accounts microservice.
pipeline.yaml & tasks.yaml – Tekton CD pipeline configuration automating source clone, code linting (Flake8), unit testing (nosetests), image build (Buildah), and deployment (oc apply) steps.



service/  
  common/        ← log and error handlers, CLI commands  
  config.py      ← Flask application configuration  
  models.py      ← SQLAlchemy model definitions  
  routes.py      ← REST API route implementations  

tests/           ← unit tests and factories  
  factories.py  
  test_cli_commands.py  
  test_models.py  
  test_routes.py  

deploy/          ← Kubernetes/OpenShift manifests  
  deployment.yaml  
  service.yaml  

pvc.yaml         ← PersistentVolumeClaim for pipeline workspace  
pipeline.yaml    ← Tekton CD pipeline specification  
tasks.yaml       ← Tekton Task definitions (echo, cleanup, nose)  
Dockerfile       ← Container image build instructions  

setup.cfg        ← tooling and lint configuration  



Original source attributed to the upstream repository. Forked and enhanced according to capstone requirements.
## Author

[John Rofrano](https://www.coursera.org/instructor/johnrofrano), Senior Technical Staff Member, DevOps Champion, @ IBM Research, and Instructor @ Coursera

## License

Licensed under the Apache License. See [LICENSE](LICENSE)

## <h3 align="center"> © IBM Corporation 2022. All rights reserved. <h3/>
