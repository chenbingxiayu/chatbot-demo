FROM python:3.8-buster

# set work directory
WORKDIR /app
# set environment variables
ENV PYTHONUNBUFFERED 1

# update vm
RUN apt-get update \
    && apt-get install -y libpython3-dev default-libmysqlclient-dev build-essential \
      --no-install-recommends \
    && apt-get clean  \
    && python -m pip install --upgrade pip==21.3.1

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# copy src code
COPY . .
ENTRYPOINT ["./entrypoint.sh"]
