import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from gestion.models import Mascota, Cita, VETERINARIOS

NOMBRES = ["Firulais", "Luna", "Max", "Mishi", "Rocky", "Nala", "Toby", "Coco", "Bruno", "Lola",
           "Simba", "Kira", "Thor", "Mia", "Zeus", "Canela", "Rufo", "Pelusa", "Chispa", "Oso"]
DUENOS = ["Ana Pérez", "Luis Soto", "María Díaz", "Pedro Rojas", "Carla Núñez",
          "Jorge Vega", "Sofía Mena", "Diego Silva"]
ESPECIES = [("Perro", "Quiltro"), ("Perro", "Labrador"), ("Gato", "Siamés"), ("Gato", "Común"),
            ("Conejo", "Enano")]
MOTIVOS = ["Control anual", "Vacunación", "Vómitos desde ayer", "Revisión de piel",
           "Cojera en una pata", "Limpieza dental"]
HORAS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "15:00", "15:30"]


class Command(BaseCommand):
    help = "Crea 20 mascotas y 20 citas de prueba (dueños con prefijo [DEMO])"

    def add_arguments(self, parser):
        parser.add_argument("--borrar", action="store_true",
                            help="borra antes las mascotas [DEMO]")

    def handle(self, *args, **options):
        if options["borrar"]:
            if input('Escribe "si" para borrar los datos [DEMO]: ') != "si":
                self.stdout.write("Cancelado.")
                return
            Mascota.objects.filter(nombre_dueno__startswith="[DEMO]").delete()

        random.seed(42)
        hoy = timezone.localdate()
        vets = [v[0] for v in VETERINARIOS]
        # todas las combinaciones día/hora/veterinario, mezcladas, para no repetir ninguna
        espacios = []
        for dia in range(4):
            for hora in HORAS:
                for vet in vets:
                    espacios.append((dia, hora, vet))
        random.shuffle(espacios)

        creadas = 0
        for dia, hora, vet in espacios:
            if creadas == 20:
                break
            fecha = hoy + timedelta(days=dia)
            # si el espacio ya está ocupado (comando corrido antes), paso al siguiente
            if Cita.objects.filter(veterinario=vet, fecha=fecha, hora=hora).exists():
                continue
            especie, raza = random.choice(ESPECIES)
            mascota = Mascota.objects.create(
                nombre=NOMBRES[creadas],
                especie=especie,
                raza=raza,
                nombre_dueno="[DEMO] " + random.choice(DUENOS),
            )
            Cita.objects.create(
                mascota=mascota,
                veterinario=vet,
                fecha=fecha,
                hora=hora,
                motivo_consulta=random.choice(MOTIVOS),
            )
            creadas += 1
        self.stdout.write(f"{creadas} mascotas y citas creadas.")
