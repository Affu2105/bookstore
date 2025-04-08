from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('', views.home, name='home'),
     path('books/', views.book_list, name='book_list'),
     path("add/", views.add_book, name="add_book"),
     path('book/<int:book_id>/',  views.book_detail, name='book_detail'),
     path('book/<int:book_id>/update/', views.update_book, name='update_book'),
     path('book/delete/<int:pk>/', views.delete_book, name='delete_book'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)