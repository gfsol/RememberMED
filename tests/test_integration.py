import unittest
import requests
from app import fetch_medication_info, send_telegram_message

class TestIntegration(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"  # Cambia si usas otra URL

    def test_openfda_api(self):
        """Prueba la integración con la API de OpenFDA"""
        medication_name = "ibuprofen"
        response = requests.get(f"https://api.fda.gov/drug/label.json?search=openfda.substance_name:{medication_name}&limit=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.json())

    def test_fetch_medication_info(self):
        """Prueba la función fetch_medication_info"""
        medication_name = "ibuprofen"
        result = fetch_medication_info(medication_name)
        self.assertIn("Información del Medicamento", result)

    def test_telegram_api(self):
        """Prueba la integración con la API de Telegram"""
        token = "FAKE_TELEGRAM_TOKEN"
        chat_id = "123456789"
        message = "Prueba de integración con Telegram"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=payload)
        self.assertIn(response.status_code, [200, 401])  # 401 si el token es inválido

    def test_send_telegram_message(self):
        """Prueba la función send_telegram_message"""
        token = "FAKE_TELEGRAM_TOKEN"
        chat_id = "123456789"
        message = "Prueba de mensaje desde send_telegram_message"
        success = send_telegram_message(token, chat_id, message)
        self.assertFalse(success)  # El token es falso, así que debe fallar

if __name__ == '__main__':
    unittest.main()