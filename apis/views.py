from rest_framework import permissions
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from apis.models import DemoTable
from apis.serializers import DemoTableSerializer


class DemoTableAPIView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = DemoTable.objects.all()
    serializer_class = DemoTableSerializer


class DemoTableByIdAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    queryset = DemoTable.objects.all()
    serializer_class = DemoTableSerializer
