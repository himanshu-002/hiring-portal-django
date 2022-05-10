from django.urls import path
from apis import views

urlpatterns = [
    path(
        'api/v1/demo/type/',
        views.DemoTableAPIView.as_view()
    ),
    path(
        'api/v1/demo/type/<str:pk>/',
        views.DemoTableByIdAPIView.as_view()
    ),
]
