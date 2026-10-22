from datetime import datetime

from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from .forms import MascotaForm, CitaForm
from .models import Cita


@login_required
def lista_citas(request):
    # por defecto hoy; si la fecha del GET no sirve, también hoy
    fecha = timezone.localdate()
    texto = request.GET.get("fecha")
    if texto:
        try:
            fecha = datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Fecha no válida, se muestran las citas de hoy.")
    citas = Cita.objects.filter(fecha=fecha).order_by("hora")
    return render(request, "gestion/lista_citas.html", {"citas": citas, "fecha": fecha})


@login_required
def registrar(request):
    if request.method == "POST":
        form_m = MascotaForm(request.POST)
        form_c = CitaForm(request.POST)
        if form_m.is_valid() and form_c.is_valid():
            mascota = form_m.save()
            cita = form_c.save(commit=False)
            cita.mascota = mascota
            try:
                cita.full_clean()
                cita.save()
            except ValidationError as e:
                # si la cita falla, borro la mascota que acabo de crear
                mascota.delete()
                form_c.add_error(None, e)
            else:
                messages.success(request, "Paciente y cita registrados.")
                return redirect("lista_citas")
    else:
        form_m = MascotaForm()
        form_c = CitaForm()
    return render(request, "gestion/registrar.html", {"form_m": form_m, "form_c": form_c})
