# seed.py
import random
import json
from django.contrib.auth.models import User
from gestion_escolar_api.models import Administradores, Maestros, Alumnos  # cambia 'tu_app' por el nombre real

# --- Datos de ejemplo ---
nombres = ["Carlos", "María", "Juan", "Ana", "Luis", "Laura", "Pedro", "Sofía", "Miguel", "Elena"]
apellidos = ["García", "López", "Martínez", "González", "Rodríguez", "Pérez", "Sánchez", "Torres", "Ramírez", "Flores"]
carreras = [
    "Ingeniería en Ciencias de la Computación",
    "Ingeniería en Tecnologías de la Información",
    "Licenciatura en Ciencias de la Computación"
]
areas = ["Inteligencia Artificial", "Redes y Telecomunicaciones", "Ingeniería de Software"]
materias_disponibles = [
    "Aplicaciones Web", "Programación 1", "Bases de datos",
    "Tecnologías Web", "Minería de datos", "Desarrollo móvil",
    "Estructuras de datos", "Administración de redes",
    "Ingeniería de Software", "Administración de S.O."
]

def nombre_random():
    return random.choice(nombres), random.choice(apellidos)

def email_random(first, last, suffix):
    return f"{first.lower()}.{last.lower()}{suffix}@example.com"

def materias_random():
    seleccion = random.sample(materias_disponibles, random.randint(2, 5))
    return json.dumps(seleccion)

# --- Seed Administradores ---
print("Creando administradores...")
for i in range(1, 51):
    first, last = nombre_random()
    email = email_random(first, last, f"_admin{i}")
    user = User.objects.create_user(
        username=f"admin_{i}",
        password="Admin1234!",
        first_name=first,
        last_name=last,
        email=email
    )
    Administradores.objects.create(
        user=user,
        clave_admin=f"ADM-{i:03d}",
        telefono=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
        rfc=f"RFC{first[:2].upper()}{last[:2].upper()}{random.randint(100000,999999)}",
        edad=random.randint(25, 55),
        ocupacion=random.choice(["Coordinador", "Director", "Supervisor", "Jefe de área"])
    )

print("✅ 50 administradores creados")

# --- Seed Maestros ---
print("Creando maestros...")
for i in range(1, 51):
    first, last = nombre_random()
    email = email_random(first, last, f"_maestro{i}")
    user = User.objects.create_user(
        username=f"maestro_{i}",
        password="Maestro1234!",
        first_name=first,
        last_name=last,
        email=email
    )
    Maestros.objects.create(
        user=user,
        id_trabajador=f"TRAB-{i:03d}",
        fecha_nacimiento=f"{random.randint(1970,1990)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        telefono=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
        rfc=f"RFC{first[:2].upper()}{last[:2].upper()}{random.randint(100000,999999)}",
        cubiculo=f"C-{random.randint(1,50):02d}",
        area_investigacion=random.choice(areas),
        materias_array=materias_random()
    )

print("✅ 50 maestros creados")

# --- Seed Alumnos ---
print("Creando alumnos...")
for i in range(1, 51):
    first, last = nombre_random()
    email = email_random(first, last, f"_alumno{i}")
    user = User.objects.create_user(
        username=f"alumno_{i}",
        password="Alumno1234!",
        first_name=first,
        last_name=last,
        email=email
    )
    Alumnos.objects.create(
        user=user,
        matricula=f"MAT{i:05d}",
        fecha_nacimiento=f"{random.randint(1998,2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        telefono=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
        curp=f"CURP{first[:2].upper()}{last[:2].upper()}{random.randint(100000,999999):06d}XX",
        carrera=random.choice(carreras),
        materias_json=materias_random()
    )

print("✅ 50 alumnos creados")
print("🎉 Seed completo: 150 usuarios en total")