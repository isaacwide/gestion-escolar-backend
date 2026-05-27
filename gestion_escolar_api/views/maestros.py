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




class MaestrosView(generics.CreateAPIView):

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
            admin = Maestros.objects.create(user=user,
                                            telefono= request.data['telefono'],
                                            id_trabajador = request.data['id_trabajador'],
                                            rfc= request.data["rfc"].upper(),
                                            cubiculo = request.data['cubiculo'],
                                            area_investigacion = request.data['area_investigacion'],
                                            fecha_nacimiento = timezone.make_aware(parse(request.data['fecha_nacimiento'])),
                                            materias_array = request.data['materias_array'],
                                            campus = request.data['campus'],
                                            sueldo = request.data['sueldo'] )
            admin.save()

            return Response({"Maestro  creado ID": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request , *args, **kwargs):

        maestro = Maestros.objects.filter(id=request.GET.get("id"),user__is_active=1).first()

        if not maestro:
            return Response({"message": "maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        serializers = MaestrosSerializer(maestro)

        return Response(serializers.data,status.HTTP_200_OK)
    
    @transaction.atomic
    def put(self, request , *args, **kwargs):

        maestro = Maestros.objects.filter(id=request.data["id"],user__is_active=1).first()

        if not maestro:
            return Response({"message": "maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        user = maestro.user

        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        # datos no tan importantes 
        maestro.id_trabajador = request.data["id_trabajador"]
        maestro.fecha_nacimiento = request.data["fecha_nacimiento"]
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"]
        maestro.cubiculo = request.data["cubiculo"]
        maestro.area_investigacion = request.data["area_investigacion"]
        maestro.materias_array = request.data["materias_array"]
        maestro.campus = request.data['campus']
        maestro.sueldo = request.data['sueldo']

        maestro.save()

        return Response({"message": "maestro actualizado correctamente"}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
        try:
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"},200)
        except Exception as e:
            return Response({"details":"Error al eliminar maestro"},400)


class MaestrosAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        maestro = Maestros.objects.filter(user__is_active = 1).order_by("id")
        lista = MaestrosSerializer(maestro, many=True).data  # noqa: F405
        return Response(lista, 200)