import logging
from typing import List

import requests
from django.conf import settings

import zulip

logger = logging.getLogger('django')


class ZulipClient:
    def __init__(self, config_file):
        logger.info(f"start client")
        self.client = zulip.Client(config_file=config_file)
        logger.info(f"end client")
        self.admin_email = settings.ZULIP['ZULIP_ADMIN_EMAIL']
        logger.info(self.admin_email)
        self.domain_url = settings.ZULIP['ZULIP_DOMAIN_URL']
        logger.info(self.domain_url)
        # self.ssl_path = settings.ZULIP['ZULIP_SSL_PATH']

    def get_users(self):
        logger.info(zulip.__file__)
        users = self.client.get_users()

        if users['result'] == 'error':
            raise Exception('Cannot get users : {error}'.format(
                error=users['msg']))
        return users

    def create_user(self, username, name):
        data = {
            "email": username,
            "password": username,
            'full_name': name,
            'short_name': name,
        }

        response = self.client.create_user(data)
        if response['result'] == 'error':
            raise Exception('Cannot create user {username}: {error}'.format(
                username=username, error=response['msg']))

        return True

    def create_stream(self, stream_name: str, user_ids: List[str]):
        user_ids.append(self.admin_email)

        response = self.client.add_subscriptions(
            streams=[
                {"name": stream_name,
                 "description": "Stream for {name}".format(name=stream_name)},
            ],
            principals=user_ids,
            invite_only=True,
            authorization_errors_fatal=False,
        )
        if response['result'] == 'error':
            raise Exception('Cannot subsribe a steam: {error}'.format(
                error=response['msg']))
        return stream_name

    def fetch_user_api_key(self, username: str, password: str):
        logger.info(self.admin_email)
        logger.info(self.domain_url)

        payload = {
            "username": username,
            "password": password,
        }

        # TODO
        # replace the url
        response = requests.post(self.domain_url + "/api/v1/fetch_api_key",
                                 data=payload)
        #  data=payload, verify=self.ssl_path)
        result = response.json()
        logger.info(response)
        logger.info("result")
        logger.info(result)
        if response.status_code != 200:
            raise Exception("Cannot get {username}'s api key: {error}".format(
                username=username, error=result['msg']))

        return result['api_key']

    def get_user_presence(self, email: str):
        response = self.client.get_user_presence(email)
        print(response)
        return

    def subscribe_stream(self, stream_name, subscribers: List[str]):
        subscribers.append(self.admin_email)
        response = self.client.add_subscriptions(
            streams=[
                {"name": stream_name}
            ],
            principals=subscribers,
            invite_only=True,
            authorization_errors_fatal=False,
        )
        logger.info(response)

        if response['result'] == 'error':
            error_msg = response['msg']
            logger.error(f'subscribe {stream_name} failed: {error_msg}')
            raise Exception(f'Cannot create new stream: {error_msg}')

        return response

    def unsubscribe_stream(self, stream_name: str, unsubscribers: List[str]):
        response = self.client.remove_subscriptions(
            [stream_name],
            principals=unsubscribers,
        )

        return response

    def get_stream_id(self, stream_name):
        response = self.client.get_stream_id(stream_name)
        if response['result'] == 'error':
            error_msg = response['msg']
            logger.error(f'stream name: {stream_name} not found when get stream id: {error_msg}')
            return None
        return response['stream_id']

    def delete_stream(self, stream_id):
        response = self.client.delete_stream(stream_id)
        return response

    def delete_stream_in_topic(self, stream_id, topic):
        response = self.client.call_endpoint(
            url=f'streams/{stream_id}/delete_topic',
            method='POST',
            request={
                'topic_name': topic,
                'stream_id': stream_id,
            }
        )
        return response
