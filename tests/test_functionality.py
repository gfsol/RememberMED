import unittest
from flask import Flask
from app import app, calculate_dosage_times

class TestFunctionality(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_page(self):
        """Prueba que la página principal se cargue correctamente"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'RememberMed', response.data)

    def test_premium_page(self):
        """Prueba que la página de funciones premium se cargue correctamente"""
        response = self.app.get('/premium')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Desbloquea funciones premium', response.data)

    def test_calculate_dosage_times(self):
        """Prueba la función de cálculo de horarios de dosis"""
        start_time = "08:00"
        hours_between = 4
        doses = 3
        expected_times = ["08:00", "12:00", "16:00"]
        self.assertEqual(calculate_dosage_times(start_time, hours_between, doses), expected_times)

    def test_telegram_webhook_start(self):
        """Prueba el webhook de Telegram con el comando /start"""
        response = self.app.post('/telegram', json={
            "message": {
                "chat": {"id": "123456"},
                "text": "/start"
            }
        }, query_string={"token": "FAKE_TELEGRAM_TOKEN"})
        self.assertEqual(response.status_code, 200)

    def test_telegram_webhook_set_reminder(self):
        """Prueba el flujo de establecer recordatorio en el webhook de Telegram"""
        response = self.app.post('/telegram', json={
            "message": {
                "chat": {"id": "123456"},
                "text": "1. Establecer recordatorio"
            }
        }, query_string={"token": "FAKE_TELEGRAM_TOKEN"})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()