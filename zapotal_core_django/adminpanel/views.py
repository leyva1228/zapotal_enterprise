from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Usuario,
    Comunero,
    Categoria,
    Noticia,
    Evento,
    Comentario,
    Reaccion,
    Mensaje,
    Notificacion,
    Multimedia,
    Autoridad,
    ContactoMensaje,
    LibroReclamacion
)

from .serializers import (
    UsuarioSerializer,
    ComuneroSerializer,
    CategoriaSerializer,
    NoticiaSerializer,
    EventoSerializer,
    ComentarioSerializer,
    ReaccionSerializer,
    MensajeSerializer,
    NotificacionSerializer,
    MultimediaSerializer,
    AutoridadSerializer,
    ContactoMensajeSerializer,
    LibroReclamacionSerializer,
    LoginSerializer
)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class ComuneroViewSet(viewsets.ModelViewSet):
    queryset = Comunero.objects.all()
    serializer_class = ComuneroSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all()
    serializer_class = NoticiaSerializer


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer


class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer


class ReaccionViewSet(viewsets.ModelViewSet):
    queryset = Reaccion.objects.all()
    serializer_class = ReaccionSerializer


class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje.objects.all()
    serializer_class = MensajeSerializer


class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer

    def get_queryset(self):
        usuario_id = self.request.query_params.get("usuario_id")

        if not usuario_id:
            return Notificacion.objects.none()

        try:
            usuario = Usuario.objects.get(id=usuario_id)

        except Usuario.DoesNotExist:
            return Notificacion.objects.none()

        queryset = Notificacion.objects.filter(
            tipo="GLOBAL"
        )

        if usuario.tipo_usuario == "COMUNERO":

            queryset = queryset | Notificacion.objects.filter(
                tipo="COMUNEROS"
            )

        queryset = queryset | Notificacion.objects.filter(
            tipo="PERSONAL",
            usuario_destino=usuario
        )

        return queryset.order_by("-fecha")


class MultimediaViewSet(viewsets.ModelViewSet):
    queryset = Multimedia.objects.all()
    serializer_class = MultimediaSerializer




class AutoridadViewSet(viewsets.ModelViewSet):
    queryset = Autoridad.objects.all()
    serializer_class = AutoridadSerializer


class ContactoMensajeViewSet(viewsets.ModelViewSet):
    queryset = ContactoMensaje.objects.all()
    serializer_class = ContactoMensajeSerializer


class LibroReclamacionViewSet(viewsets.ModelViewSet):
    queryset = LibroReclamacion.objects.all()
    serializer_class = LibroReclamacionSerializer
    permission_classes = [AllowAny]


# ==========================
# LOGIN DE USUARIOS
# ==========================

@api_view(["POST"])
@permission_classes([AllowAny])

def login_usuario(request):

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():

        email = serializer.validated_data["email"]

        password = serializer.validated_data["password"]

        try:

            usuario = Usuario.objects.get(email=email)

        except Usuario.DoesNotExist:

            return Response(
                {
                    "ok": False,
                    "mensaje": "Correo o contraseña incorrectos."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if usuario.password != password:

            return Response(
                {
                    "ok": False,
                    "mensaje": "Correo o contraseña incorrectos."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if usuario.estado != Usuario.EstadoUsuario.ACTIVO:

            return Response(
                {
                    "ok": False,
                    "mensaje": "El usuario se encuentra inactivo."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "ok": True,
                "mensaje": "Inicio de sesión correcto.",

                "usuario": {
                    "id": usuario.id,
                    "nombres": usuario.nombres,
                    "apellidos": usuario.apellidos,
                    "email": usuario.email,
                    "dni": usuario.dni,
                    "tipo_usuario": usuario.tipo_usuario,
                    "estado": usuario.estado,
                    "dni_verificado": usuario.dni_verificado,

                    "foto_perfil":
                    request.build_absolute_uri(
                        usuario.foto_perfil.url
                    ) if usuario.foto_perfil else None,
                }
            },

            status=status.HTTP_200_OK
        )

    return Response(
        {
            "ok": False,
            "errores": serializer.errors
        },

        status=status.HTTP_400_BAD_REQUEST
    )