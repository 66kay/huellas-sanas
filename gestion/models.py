from django.core.exceptions import ValidationError
from django.db import models

# Lista fija de veterinarios de la clínica
VETERINARIOS = [
    ("Dra. Paula Rojas", "Dra. Paula Rojas"),
    ("Dr. Andrés Soto", "Dr. Andrés Soto"),
    ("Dra. Camila Fuentes", "Dra. Camila Fuentes"),
]


class Mascota(models.Model):
    nombre = models.CharField(max_length=60)
    especie = models.CharField(max_length=40)
    raza = models.CharField(max_length=60)
    nombre_dueno = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.nombre_dueno})"


class Cita(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("atendida", "Atendida"),
        ("cancelada", "Cancelada"),
    ]

    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.CharField(max_length=60, choices=VETERINARIOS)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo_consulta = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default="pendiente")

    def clean(self):
        # el motivo no puede ser solo espacios
        if not self.motivo_consulta or not self.motivo_consulta.strip():
            raise ValidationError({"motivo_consulta": "El motivo de consulta es obligatorio."})
        # busco otra cita activa del mismo veterinario a la misma fecha y hora
        if self.estado != "cancelada":
            cruce = Cita.objects.filter(
                veterinario=self.veterinario, fecha=self.fecha, hora=self.hora
            ).exclude(pk=self.pk).exclude(estado="cancelada")
            if cruce.exists():
                raise ValidationError("Ese veterinario ya tiene una cita a esa hora.")

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha} {self.hora}"
