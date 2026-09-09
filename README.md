# Helpdesk Ticket Management System

## Overview

A Flask-based IT Helpdesk Ticket Management System for managing
support tickets within a UK organisation.

## Features

- Create tickets
- View tickets
- Update tickets
- Delete tickets
- Search by Ticket ID and Title
- Filter by Priority, Status and Category
- Combined search and filters
- Dynamic dashboard statistics
- Input validation
- Error handling
- SQLite database
- Automated tests

## Technologies

- Python
- Flask
- SQLite
- HTML
- CSS
- Jinja2
- Pytest

## Project Structure

helpdesk-ticket-system/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── helpdesk.db
├── database/
├── services/
├── templates/
├── static/
└── tests/

## Installation

Create and activate the virtual environment:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

## Run the Application

python app.py

Open:

http://127.0.0.1:5000

## Run Tests

pytest -v