### 1. Deploy Django server

Put `.env.docker` file with all your environment variables under the same directory with `docker-compose.yml`. Please
don't push `.env.docker` file to this repo. Build django server first.

```shell
docker-compose up -d --build django
```

Stop Django and move to next step.

```shell
docker-compose stop django
```

### 2. Create Database/ Database Migration

In local/UAT/prod environment, operator should use django cli to migrate change to database.

Formal migration is described in [django_database_migration.md](./django_database_migration.md)

However, in production database, the migration status is polluted, cannot be done using django cli.

Operator may consider

1. Delete all tables and migrate the database from the _nothing.
   (❗❗ admin account and user groups will be deleted and need to re-create,
   see [#5](./setup_django.md#5-create-superuser-for-django-server),
   [#6](./setup_django.md#6-add-user-group))
2. Manually alternate the existing database.

### 3. Enable Server Side Encryption

If database/tables are newly created, run this sql commands [enable_TDE](./enable_TDE.sql) to
enable [Transparent Data Encryption (TDE)](https://www.mysql.com/products/enterprise/tde.html).

### 4. Grant privilege to db user

Get into mysql and grant `MYSQL_USER` DBA role

![dba_role](img/dba.png)

### 5. Create superuser for django server

Please create and activate virtual environment before running the following

```shell
cd chatbot_demo
chmod +x manage_cli.sh
./manage_cli.sh createsuperuser

# Run test if needed
./manage_cli.sh test tasks.tests
./manage_cli.sh test main.tests.test_login

# After creating superuser successfully
cd ../
docker-compose up -d --build django
```

Login [admin_page](http://localhost:8899/admin/) with the superuser you just created.

### 6. Add User Group

We will add three user groups, `app_admin`, `supervisor` and `counsellor`.

`administrator` will be granted `app_admin`.

`supervisor` will be granted `supervisor`.

`online triage`, `DO` and `counsellor` will be granted `counsellor`.

app_admin
![app_admin.png](img/app_admin.png)

counsellor
![counsellor.png](img/counsellor.png)

### 7. Add Staff User

Add staff
![add_staff](img/add_staff.png)

Assign group to users (access rights)
![assign_groups.png](img/assign_groups.png)

### 8. Run All service

```shell
# Deploy backend only
docker-compose up -d --build django celery celery_beat
# mysql is for local development use, while flower is optional to run.

# Deploy frontend and backend
./deploy.sh
```

   