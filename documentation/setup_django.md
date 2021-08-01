1. Deploy Django server 
   
    Put `.env.docker` file with all your environment variables under the same directory with `docker-compose.yml`.
    Please don't push `.env.docker` file to this repo.
    Build django server first.
    ```shell
    docker-compose up -d --build django
    ```
    Then the database will be created together with user defined as `MYSQL_USER`.

    Stop Django and move to next step.
    ```shell
    docker-compose stop django
    ```

2. Grant privilege to db user
    
    Get into mysql and grant `MYSQL_USER` DBA role
   
   ![dba_role](img/dba.png)
   
3. Create superuser for django server

   ```shell
   cd chatbot_demo
   ./manage_cli.py createsuperuser
   
   # Run test if needed
   ./manage_cli.py test tasks.tests
   
   # After creating superuser successfully
   cd ../
   docker-compose up -d --build django
   ```
   Login `http://localhost:8899/admin/` with `username=admin` and `password=admin`

4. Add User Group
   
   We will add two user groups, `app_admin` and `counsellor`.
   `administrator` and `supervisor` will be granted `app_admin`. 
   `online triage`, `DO` and `counsellor` will be granted `counsellor`. 

   app_admin
   ![app_admin.png](img/app_admin.png)
   
   counsellor
   ![counsellor.png](img/counsellor.png)

5. Add Staff User
   
   Add staff
   ![add_staff](img/add_staff.png)

   Assign user group (assign rights)
   ![assign_groups.png](img/assign_groups.png)
   
6. Run All service

   ```shell
   docker-compose up -d --build
   ```