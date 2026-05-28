from django.db.models import *
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from dateutil.parser import parse
from django.contrib.auth.models import User, Group
from gestion_escolar_api.models import *
from gestion_escolar_api.serializers import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response



class AlumnoAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        alumno = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnosSerializer(alumno, many=True).data  # noqa: F405
        return Response(lista, 200)

class Alumnoview(generics.CreateAPIView):

    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        
        # Serializamos los datos del administrador para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            matricula = request.data['matricula']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
    
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Nombre de usuario "+email+", ya existe"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            #Cifrar la contraseña
            user.set_password(password)
            user.save()

            #Asignar el rol al usuario a la tabla de grupos
            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Almacenar los datos adicionales del administrador en la tabla de administradores
            admin = Alumnos.objects.create(user=user,
                                            matricula=matricula,
                                            telefono= request.data['telefono'],
                                            curp= request.data["curp"].upper(),
                                            carrera = request.data['carrera'],
                                            fecha_nacimiento = timezone.make_aware(parse(request.data['fecha_nacimiento'])),
                                            materias_json = request.data['materias_json'],
                                            direccion = request.data['direccion'],
                                            sexo = request.data['sexo']
                                            )
            admin.save()

            return Response({"Alumno  creado ID": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        alumno = Alumnos.objects.filter(id=request.GET.get("id"),user__is_active=1).first()
        if not alumno:
            return Response({"message": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AlumnosSerializer(alumno)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        alumno = Alumnos.objects.filter(id=request.data["id"],user__is_active=1).first()
        if not alumno:
            return Response({"message": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        user = alumno.user

        #vamos a actualizar los campos de los alumnos
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        alumno.matricula = request.data["matricula"]
        alumno.fecha_nacimiento = request.data["fecha_nacimiento"]
        alumno.telefono = request.data["telefono"]
        alumno.curp = request.data["curp"]
        alumno.carrera = request.data["carrera"]
        alumno.materias_json = request.data["materias_json"]

        alumno.direccion = request.data['direccion']
        alumno.sexo = request.data['sexo']

        alumno.save()

        return Response({"message": "Alumno actualizado correctamente"}, status=status.HTTP_200_OK)
    def delete(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            alumno.user.delete()
            return Response({"details":"Alumno eliminado"},200)
        except Exception as e:
            return Response({"details":"Error al alumno maestro"},400)

    
