from django.db.models import *
from django.db import transaction
from django.utils import timezone
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
                                            materias_array = request.data['materias_array'])
            admin.save()

            return Response({"Maestro  creado ID": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class MaestrosAll(generics.ListAPIView):
    """Vista para listar todos los maestros"""
    queryset = Maestros.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

