from django.contrib import admin
from .models import Mascota, Cita


class MascotaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especie", "raza", "nombre_dueno")
    search_fields = ("nombre", "nombre_dueno")


class CitaAdmin(admin.ModelAdmin):
    list_display = ("mascota", "veterinario", "fecha", "hora", "estado")
    list_filter = ("estado", "fecha")


admin.site.register(Mascota, MascotaAdmin)
admin.site.register(Cita, CitaAdmin)
