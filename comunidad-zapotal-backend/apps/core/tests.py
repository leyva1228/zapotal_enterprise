from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import validar_dni, validar_telefono


class ValidarDniTests(TestCase):
    def test_dni_valido(self):
        self.assertEqual(validar_dni('12345678'), '12345678')

    def test_dni_con_letras(self):
        with self.assertRaises(ValidationError):
            validar_dni('1234567A')

    def test_dni_muy_corto(self):
        with self.assertRaises(ValidationError):
            validar_dni('1234567')

    def test_dni_muy_largo(self):
        with self.assertRaises(ValidationError):
            validar_dni('123456789')

    def test_dni_vacio(self):
        with self.assertRaises(ValidationError):
            validar_dni('')

    def test_dni_con_espacios(self):
        with self.assertRaises(ValidationError):
            validar_dni('1234 567')


class ValidarTelefonoTests(TestCase):
    def test_telefono_valido(self):
        self.assertEqual(validar_telefono('987654321'), '987654321')

    def test_telefono_vacio(self):
        self.assertEqual(validar_telefono(''), '')

    def test_telefono_con_letras(self):
        with self.assertRaises(ValidationError):
            validar_telefono('98765A321')

    def test_telefono_muy_corto(self):
        with self.assertRaises(ValidationError):
            validar_telefono('12345')

    def test_telefono_largo_valido(self):
        self.assertEqual(validar_telefono('123456789012345'), '123456789012345')
