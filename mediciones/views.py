from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FlowReading
from .serializers import FlowReadingReadSerializer, FlowReadingSerializer
from .services import dashboard_payload, latest_status_payload


def serialize_user(user):
    full_name = user.get_full_name().strip()

    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'display_name': full_name or user.username,
        'is_staff': user.is_staff,
    }


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'detail': 'Debes ingresar usuario y contrasena.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {'detail': 'Usuario o contrasena incorrectos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {'detail': 'Este usuario esta inactivo.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.is_staff:
            return Response(
                {'detail': 'Tu cuenta esta pendiente de aprobacion por un administrador.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': serialize_user(user),
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        email = request.data.get('email', '').strip()
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()

        if not username or not password:
            return Response(
                {'detail': 'Debes ingresar usuario y contrasena.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(password) < 8:
            return Response(
                {'detail': 'La contrasena debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            return Response(
                {'detail': 'Ese nombre de usuario ya existe.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
        )

        return Response(
            {
                'detail': 'Cuenta creada. Un administrador debe aprobar tu acceso.',
                'user': serialize_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'user': serialize_user(request.user)})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FlowReadingListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = min(int(request.query_params.get('limit', 100)), 500)
        queryset = FlowReading.objects.order_by('-fecha')[:limit]
        serializer = FlowReadingReadSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FlowReadingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save()
        return Response(
            FlowReadingReadSerializer(reading).data,
            status=status.HTTP_201_CREATED,
        )


class LatestFlowReadingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        payload = latest_status_payload()
        reading = payload.pop('reading')
        payload['reading'] = FlowReadingReadSerializer(reading).data if reading else None
        return Response(payload)


class DashboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        payload = dashboard_payload()
        latest_reading = payload['latest'].pop('reading')
        payload['latest']['reading'] = (
            FlowReadingReadSerializer(latest_reading).data if latest_reading else None
        )
        payload['recent_readings'] = FlowReadingReadSerializer(
            payload['recent_readings'],
            many=True,
        ).data
        payload['active_alerts'] = FlowReadingReadSerializer(
            payload['active_alerts'],
            many=True,
        ).data
        return Response(payload)


class AlertsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = min(int(request.query_params.get('limit', 100)), 500)
        queryset = FlowReading.objects.exclude(alerta='').order_by('-fecha')[:limit]
        serializer = FlowReadingReadSerializer(queryset, many=True)
        return Response(serializer.data)
