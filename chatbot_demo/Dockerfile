FROM python:3.8

ARG BUILD_DIR

COPY ${BUILD_DIR} /code/chatbot_demo

RUN cd /code/chatbot_demo && \
    pip install -r requirements.txt

RUN chgrp -R 0 /code/chatbot_demo && \
    chmod -R g=u /code/chatbot_demo