from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Mascota, Cita

VET1 = "Dra. Paula Rojas"
VET2 = "Dr. Andrés Soto"


class CitaTests(TestCase):
    def setUp(self):
        self.mascota = Mascota.objects.create(
            nombre="Luna", especie="Perro", raza="Quiltro", nombre_dueno="Ana")
        self.hoy = timezone.localdate()

    def crear(self, vet=VET1, estado="pendiente", motivo="Vacunación"):
        return Cita(mascota=self.mascota, veterinario=vet, fecha=self.hoy, hora="10:00",
                    motivo_consulta=motivo, estado=estado)

    def test_motivo_vacio_es_invalido(self):
        with self.assertRaises(ValidationError):
            self.crear(motivo="   ").full_clean()

    def test_cruce_mismo_veterinario(self):
        self.crear().save()
        with self.assertRaises(ValidationError):
            self.crear().full_clean()

    def test_otro_veterinario_es_valido(self):
        self.crear().save()
        self.crear(vet=VET2).full_clean()

    def test_cancelada_no_bloquea(self):
        self.crear(estado="cancelada").save()
        self.crear().full_clean()


class VistasTests(TestCase):
    def setUp(self):
        User.objects.create_user("recep", password="clave12345")
        self.mascota = Mascota.objects.create(
            nombre="Luna", especie="Perro", raza="Quiltro", nombre_dueno="Ana")
        self.hoy = timezone.localdate()

    def datos_registro(self, fecha, motivo="Control anual"):
        return {"nombre": "Max", "especie": "Gato", "raza": "Común", "nombre_dueno": "Luis",
                "fecha": fecha.isoformat(), "hora": "11:00", "veterinario": VET1,
                "motivo_consulta": motivo}

    def test_listado_sin_login_redirige(self):
        r = self.client.get(reverse("lista_citas"))
        self.assertRedirects(r, "/accounts/login/?next=/")

    def test_listado_muestra_solo_hoy(self):
        Cita.objects.create(mascota=self.mascota, veterinario=VET1, fecha=self.hoy,
                            hora="10:00", motivo_consulta="Motivo de hoy")
        Cita.objects.create(mascota=self.mascota, veterinario=VET1,
                            fecha=self.hoy + timedelta(days=1), hora="10:00",
                            motivo_consulta="Motivo de mañana")
        self.client.login(username="recep", password="clave12345")
        r = self.client.get(reverse("lista_citas"))
        self.assertContains(r, "Motivo de hoy")
        self.assertNotContains(r, "Motivo de mañana")

    def test_fecha_invalida_no_da_error(self):
        self.client.login(username="recep", password="clave12345")
        r = self.client.get(reverse("lista_citas"), {"fecha": "basura"})
        self.assertEqual(r.status_code, 200)

    def test_registro_valido_crea_mascota_y_cita(self):
        self.client.login(username="recep", password="clave12345")
        r = self.client.post(reverse("registrar"), self.datos_registro(self.hoy))
        self.assertRedirects(r, reverse("lista_citas"))
        self.assertTrue(Mascota.objects.filter(nombre="Max").exists())
        self.assertEqual(Cita.objects.count(), 1)

    def test_registro_fecha_pasada_se_rechaza(self):
        self.client.login(username="recep", password="clave12345")
        r = self.client.post(reverse("registrar"),
                             self.datos_registro(self.hoy - timedelta(days=1)))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Mascota.objects.filter(nombre="Max").exists())

    def test_registro_con_cruce_no_deja_mascota(self):
        Cita.objects.create(mascota=self.mascota, veterinario=VET1, fecha=self.hoy,
                            hora="11:00", motivo_consulta="Otra consulta")
        self.client.login(username="recep", password="clave12345")
        r = self.client.post(reverse("registrar"), self.datos_registro(self.hoy))
        self.assertContains(r, "Ese veterinario ya tiene una cita a esa hora")
        self.assertFalse(Mascota.objects.filter(nombre="Max").exists())

    def test_motivo_corto_se_rechaza(self):
        self.client.login(username="recep", password="clave12345")
        self.client.post(reverse("registrar"), self.datos_registro(self.hoy, "abc"))
        self.assertEqual(Cita.objects.count(), 0)


class GenerarDatosTests(TestCase):
    def test_crea_20_mascotas_y_citas(self):
        call_command("Generar_Datos")
        self.assertEqual(Mascota.objects.count(), 20)
        self.assertEqual(Cita.objects.count(), 20)
