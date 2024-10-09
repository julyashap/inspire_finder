from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@test.com", password="password", phone="81234567890")
        self.user.is_active = True
        self.user.code = "1234"
        self.user.save()

    def test_registration_valid_data(self):
        data = {
            'email': 'new_user@test.com',
            'password1': 'new_password',
            'password2': 'new_password',
            'phone': '81234567890'
        }
        response = self.client.post(reverse('users:user_registration'), data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='new_user@test.com').exists())

    def test_phone_confirmation_valid(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(reverse('users:phone_confirm'), {'code': '1234'})
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.is_active)

    def test_phone_confirmation_invalid(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(reverse('users:phone_confirm'), {'code': '9999'})
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.user.is_active)

    def test_user_detail_view(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('users:user_detail', args=[self.user.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)

    def test_user_update_view(self):
        self.client.force_login(user=self.user)
        data = {
            'first_name': 'UpdatedName',
            'last_name': 'UpdatedLastName',
            'email': 'updated@test.com',
            'phone': '81234567891',
        }
        response = self.client.post(reverse('users:user_update', args=[self.user.pk]), data)

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@test.com')

    def test_user_delete_view(self):
        self.client.force_login(user=self.user)

        response = self.client.delete(reverse('users:user_delete', args=[self.user.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
