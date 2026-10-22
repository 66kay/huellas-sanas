# Huellas Sanas

Sistema de citas para una clínica veterinaria hecho con Django. Permite ver las citas de un día y registrar un paciente nuevo junto con su cita.

## Cómo ejecutarlo

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py Generar_Datos
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ e ingresar con el usuario creado. El admin está en /admin/.

Variables opcionales (ver `.env.example`): `DJANGO_SECRET_KEY` y `DJANGO_DEBUG`.
Si no se definen, se usan valores solo para desarrollo.

## Datos de prueba

`python manage.py Generar_Datos` crea 20 mascotas (dueños con prefijo `[DEMO]`) y 20 citas entre hoy y 3 días después.
Con `--borrar` pide escribir "si" y elimina solo las mascotas `[DEMO]` (y sus citas) antes de crear las nuevas.

## Pruebas

```
python manage.py test gestion
```

## Mejoras respecto a la consigna

1. **Veterinario en la cita.** Cada cita tiene un veterinario (lista fija de tres) y la lista diaria lo muestra. Así ningún paciente queda sin saber quién lo atiende y cada profesional ve su agenda.
2. **Validación de cruce de horario.** `Cita.clean()` rechaza una cita si el mismo veterinario ya tiene otra a la misma fecha y hora (las canceladas no cuentan). Evita que dos pacientes lleguen a la misma hora con el mismo veterinario.
3. **Motivo de consulta obligatorio (mínimo 5 caracteres).** Se valida en el formulario, y el modelo rechaza motivos vacíos. Evita citas sin información sobre qué atender, que es un dato que se perdía.

Además, la fecha de una cita nueva no puede ser pasada, y si la cita falla la validación la mascota recién creada se borra.
