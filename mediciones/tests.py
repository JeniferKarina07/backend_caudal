from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import FlowReading


class FlowReadingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_normal_reading_from_esp32_payload(self):
        response = self.client.post(
            reverse('flow-readings'),
            {'caudal_entrada': 10.5},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(FlowReading.objects.count(), 1)
        self.assertEqual(response.data['estado'], FlowReading.Status.NORMAL)
        self.assertEqual(response.data['origen_dato'], FlowReading.Source.ESP32)

    def test_zero_flow_generates_dry_alert(self):
        response = self.client.post(
            reverse('flow-readings'),
            {'caudal_entrada': 0},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['estado'], FlowReading.Status.SECO)
        self.assertTrue(response.data['alerta'])

    def test_dashboard_returns_monitoring_summary(self):
        FlowReading.objects.create(caudal_entrada=12, estado=FlowReading.Status.NORMAL)

        response = self.client.get(reverse('flow-dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('latest', response.data)
        self.assertIn('stats', response.data)
