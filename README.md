# Hiring Portal
<img src="https://img.shields.io/badge/Python-3.8.10-blue.svg" height="30"></img> 
<img src="https://img.shields.io/badge/Django-3.1.7-blue.svg" height="30"></img> 
<img src="https://img.shields.io/badge/Django%20Rest%20Framework-3.12.4-blue.svg" height="30"></img>
<hr/>


This is the Backend setup guide for the project Hiring Portal.
## Installation

Before you begin, ensure you have met the following requirements:

* Database creation and setup:
    ```
    $ sudo mysql
    
    mysql> CREATE DATABASE HiringPortal;
    
    # Creating new MySql user (Optional)
    mysql> CREATE USER '<username>'@'localhost' IDENTIFIED BY '<password>';
    
    # Granting privileges to the new/existing user
    mysql> GRANT ALL PRIVILEGES ON *.* TO '<username>'@'localhost' WITH GRANT OPTION;
    ```

* Steps to configure the backend and run the project
  1. Create/Activate virtualenv
  2. Install required packages
      ```bash
      pip install -r requirements.txt
      ```
  3. Add `.env` file to the project, you can refer to `.env.template`, copy and change Db Config accordingly. 
  4. Make database migrations:
      1. ***Note***: Make sure created DB in MySQL is with the same name that you have added in the `.env` file before making migrations to avoid unexpected errors
      ```bash
      $ ./manage.py makemigrations
      $ ./manage.py migrate
      ```
     ***Warning***: if above gives some error, try installing this: `sudo apt-get install libmysqlclient-dev`, and try again
  5. Run the project
      ```bash
      $ ./manage.py runserver
      ```
  6. Create Superuser to get admin access
     ```bash
     $ ./manage.py createsuperuser
     ```

## URLs
1. Admin Panel - `{HOST}/admin`
