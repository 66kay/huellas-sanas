from django.utils import timezone

from django import forms
from .models import Mascota, Cita


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ["nombre", "especie", "raza", "nombre_dueno"]
        labels = {"nombre_dueno": "Nombre del dueño"}


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ["fecha", "hora", "veterinario", "motivo_consulta"]
        labels = {"motivo_consulta": "Motivo de consulta"}
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora": forms.TimeInput(attrs={"type": "time"}),
            "motivo_consulta": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha < timezone.localdate():
            raise forms.ValidationError("La fecha no puede ser pasada.")
        return fecha

    def clean_motivo_consulta(self):
        motivo = self.cleaned_data["motivo_consulta"].strip()
        if len(motivo) < 5:
            raise forms.ValidationError("El motivo debe tener al menos 5 caracteres.")
        return motivo
