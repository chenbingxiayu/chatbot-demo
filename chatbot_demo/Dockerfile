FROM python:3.8

# set work directory
WORKDIR /app

# update vm
RUN apt-get update
RUN apt-get install libpython3-dev default-libmysqlclient-dev build-essential -y

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
#COPY ./entrypoint.sh /app/entrypoint.sh

# copy project
COPY . /app

# run entrypoint.sh
#ENTRYPOINT ["/app/entrypoint.sh"]
