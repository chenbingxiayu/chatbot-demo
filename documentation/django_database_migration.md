## Database Migration

```shell
cd chatbot_demo
```

Create virtual environment if not exist.

```shell
python -m venv venv
```

Activate virtual environment

```shell
source venv/bin/activate
pip install -r requirements.txt
```

`manage_cli.py` serve as a proxy to run django cli. It loads the environment variable from `.env.docker` before run your
command.

```shell
# Generate migration scripts
./manage_cli.py makemigrations

# Execute migration scripts
./manage_cli.py migrate

# Rollback to certain migration step
./manage_cli.py migrate <app_name> <migration name>
./manage_cli.py migrate main 0005_previous_migration
```

You can check the migration status in table `django_migrations`

Other useful commands:

[reversing-migrations](https://docs.djangoproject.com/en/3.2/topics/migrations/#reversing-migrations)

[squash migrations](https://docs.djangoproject.com/en/3.2/topics/migrations/#migration-squashing)
   