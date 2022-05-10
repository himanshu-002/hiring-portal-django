# python-django-microservice-template
Python Django Microservice Template Repository

## How to run?
**Steps to configure and run the project**
1. Clone this repository
2. Create a virtual environment (optional but recommended)
3. Initialise pre-commit hook:
    ```bash
    pip install pre-commit && \
    pre-commit install && \
    export LC_ALL=en_US.UTF-8; export LANG=en_US.UTF-8
    ```
4. Install required packages
    ```bash
    pip install -r requirements.txt
    ```
5. Add `.env` file to the project, you can refer `.env.template`
6. Make database migrations:
    1. ***Note***: Create a DB in PostgreSQL with the same name that you have been added in the .env file before making migrations to avoid unexpected errors
    ```bash
    ./manage.py makemigrations
    ./manage.py migrate
    ```
7. Run the project
    ```bash
    ./manage.py runserver
    ```

## GitHub Standards
1. Please adhere to following standards while using GitHub
   1. Initialise pre-commit hook as mentioned in the above steps
   2. Never make any commits directly to the `master` or `develop` branch
   3. Always use `feat` and `fix` branches for adding any new feature or fixing any existing bug
   4. `feat` and `fix` branches will always be created from `develop` branch and **not from the `master` branch**
   5. Naming convention for `feat` and `fix` branches
      1. Name of `feat` and `fix` branch will be followed by the issue you are working, you can check assigned issues in [Project Dashboard](https://github.com/python-data-engineering/data-pipeline-boilerplate/projects/1)
      2. For example, if you are working on [Issue #1](https://github.com/python-data-engineering/data-pipeline-boilerplate/issues/1) then your branch name will be `feat/Issue#1` or `fix/Issue#1`. Here, `Issue` is the **tag** and `#1` is the **number** of that issue

## URLs
1. Admin Panel - `{HOST}/microservice-admin`
