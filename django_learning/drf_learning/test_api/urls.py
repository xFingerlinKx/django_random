from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.CreateUserAPIView.as_view(), name='create-user'),
    path('data/', views.GetUserDataApiView.as_view(), name='get-user-data'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('api-token-auth/', views.CustomAuthToken.as_view(), name='api-token-auth'),
    path('api-token-logout/', views.CustomAuthLogOut.as_view(), name='api-token-logout'),
]
