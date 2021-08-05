import logging
from typing import List
import zulip
import requests

from django.conf import settings


logger = logging.getLogger('django')
class ZulipClient:
    def __init__(self, config_file):
        self.client = zulip.Client(config_file=config_file)
        self.admin_email = settings.ZULIP['ADMIN_EMAIL']
        self.domain_url = settings.ZULIP['DOMAIN_URL']

    def get_users(self):
        users = self.client.get_users()
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
        payload = {
            "username": username,
            "password": password,
        }

        # TODO
        # replace the url
        response = requests.post(self.domain_url + "api/v1/fetch_api_key",
                                 data=payload, verify='./ssl/zulip.combined-chain.crt')
        result = response.json()
        if response.status_code != 200:
            raise Exception("Cannot get {username}'s api key: {error}".format(
                username=username, error=result.msg))

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
            logger.error(f'stream name: {stream_name} not found when get stream id')
            return None
        return response['stream_id']

    def delete_stream(self, stream_id):
        response = self.client.delete_stream(stream_id)
        return response


    def delete_stream_in_topic(self, stream_id, topic):
        response = self.client.call_endpoint(
            url=f'streams/{stream_id}/delete_topic',
            method='POST',
            request= {
                'topic_name': topic,
                'stream_id': stream_id,
            }
        )
        return response