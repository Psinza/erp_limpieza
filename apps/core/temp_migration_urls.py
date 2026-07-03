from django.urls import path
from .temp_migration import run_migrations_view

urlpatterns = [
    path('', run_migrations_view, name='run_migrations'),
]
