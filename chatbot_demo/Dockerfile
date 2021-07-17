FROM python:3.8-slim-buster

# set work directory
WORKDIR /app

# update vm
RUN apt-get update \
    && apt-get install -y libpython3-dev default-libmysqlclient-dev build-essential \
    && python -m pip install --upgrade pip

# install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# copy src code
COPY . /app
ENTRYPOINT ["./entrypoint.sh"]
