from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group

from main.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        admin_group = Group.objects.create(name='app_admin')
        counsellor_group = Group.objects.create(name='counsellor_group')

        admin_user = User.objects.create_user(netid='admin_user',
                                              is_active=True)
        counsellor_user = User.objects.create_user(netid='counsellor_user',
                                                   is_active=True)
        User.objects.create_user(netid='unauthorized_user',
                                 is_active=True)

        admin_group.user_set.add(admin_user)
        counsellor_group.user_set.add(counsellor_user)

    @patch('main.views.sso_auth')
    def test_sso_callback(self, mock_sso_auth):
        # test student login
        mock_sso_auth.decode.return_value = {
            "sub": "12345678A",
            "cn": "12345678A",
            "mail": "12345678A@connect.polyu.hk",
            "polyuUserType": "Student",
            "polyuCurrentStudent": ""
        }

        response = self.client.post(reverse('login_sso_callback'),
                                    data={
                                        "data": {
                                            True
                                        }
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

        # test app_admin login
        mock_sso_auth.decode.return_value = {
            "sub": "admin_user",
            "cn": "admin_user",
            "mail": "staff@uat.polyu.edu.hk",
            "polyuUserType": "Staff",
            "polyuCurrentStudent": ""
        }

        response = self.client.post(reverse('login_sso_callback'),
                                    data={
                                        "data": {
                                            True
                                        }
                                    })
        self.assertRedirects(response, reverse('login_staff'))

        # test counsellor login
        mock_sso_auth.decode.return_value = {
            "sub": "counsellor_user",
            "cn": "counsellor_user",
            "mail": "staff@uat.polyu.edu.hk",
            "polyuUserType": "Staff",
            "polyuCurrentStudent": ""
        }

        response = self.client.post(reverse('login_sso_callback'),
                                    data={
                                        "data": {
                                            True
                                        }
                                    })
        self.assertRedirects(response, reverse('login_staff'))

        # test unauthorized user login
        mock_sso_auth.decode.return_value = {
            "sub": "unauthorized_user",
            "cn": "unauthorized_user",
            "mail": "staff@uat.polyu.edu.hk",
            "polyuUserType": "Staff",
            "polyuCurrentStudent": ""
        }

        response = self.client.post(reverse('login_sso_callback'),
                                    data={
                                        "data": {
                                            True
                                        }
                                    })
        self.assertRedirects(response, reverse('login'))
