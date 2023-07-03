# Product recall alerts API

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Status](#status)

## General info
REST API allowing users to add their details to a database in order to register for food and drug recall alerts (UK products only). Users subscribe or unsubscribe for recall alerts for relevant products by adding recently purchased food or pharmaceutical products to the database. Users can also remove their details entirely if they no longer need the service.

This is the API for a personal full stack project.

## Technologies
Python 3.10

FastAPI

## Setup

1. cd to project root folder, i.e. ```cd path-to-project/recallalerts-api```

2. ```pip install requirements.txt```

3. Add the following to environment variables:

   DATABASE_URL - _Should be a postgres database_

   ORIGINS - _List of allowed origins_

   TEST_DB - _Another postgres database for tests if needed_

   GENERATED_SECRET_KEY - _Generate your own secret key_

6. run app ```uvicorn main:app --port 8080```

   (8080 can be replaced with port of your own choosing)

## Status
Still in development. Constantly refactoring.
