from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardNavigationTests(TestCase):
    def test_admin_can_open_order_management_from_sidebar(self):
        admin_user = get_user_model().objects.create_user(
            username='admin',
            email='admin@example.com',
            password='test-password',
            cpf='12345678901',
            nascimento=date(1990, 1, 1),
            is_staff=True,
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse('dashboard'))

        self.assertContains(
            response,
            f'href="{reverse("painel_pedidos")}"',
        )
