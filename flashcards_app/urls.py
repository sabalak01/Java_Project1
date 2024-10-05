from django.urls import path
from . import views

app_name = 'flashcards'  # Указываем пространство имен для URL-адресов приложения

urlpatterns = [
    path('', views.home, name='home'),
    path('decklist', views.deck_list, name='deck_list'),  # Список колод
    path('decks/new/', views.add_deck, name='add_deck'),  # Создание новой колоды
    path('decks/<int:deck_id>/', views.deck_detail, name='deck_detail'),  # Детали колоды
    path('decks/<int:deck_id>/add_flashcard/', views.add_flashcard, name='add_flashcard'),  # Создание новой карточки
    path('decks/<int:deck_id>/study/', views.study_deck, name='study_deck'),  # Изучение колоды
    path('deck/<int:deck_id>/upload/', views.upload_file, name='upload_file'),

]
