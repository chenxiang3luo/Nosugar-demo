from django.urls import path, include
from rest_framework.routers import DefaultRouter
from snippets import views

# Create a router and register our viewsets with it.
# router = DefaultRouter()
# router.register(r'phone', views.QueryViewSet,basename="query")
# router.register(r'users', views.UserViewSet,basename="user")
phone_detect = views.QueryViewSet.as_view({
    # 'get': 'detect',
    'post': 'detect_batch'
    })

phone_list = views.QueryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

phone_process = views.QueryViewSet.as_view({
    'get': 'process',
})

phone_detail = views.QueryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
register = views.UserRegistrationView.as_view({
    'post': 'register'
})
login = views.UserRegistrationView.as_view({
    'post': 'login'
})
# The API URLs are now determined automatically by the router.
urlpatterns = [
    # path('api/', include(router.urls)),
    # path('token/',snippet_highlight),
    path('phone/',phone_list),
    path('detect/',phone_detect),
    path('phone/<int:pk>/',phone_detail),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('detect/<int:pk>/process/', phone_process, name='process'),
]