from dill.pointers import refobject
from django.contrib.gis.db.backends.postgis.pgraster import chunk
from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from .models import Deck, Flashcard,UserProgress
from .forms import DeckForm, FlashcardForm
from django.utils import timezone
from .forms import UploadFileForm
from django.http import HttpResponseRedirect
from django.db.models import F
import requests
import cohere


def home(request):
    return render(request, 'flashcards_app/index.html')


def deck_list(request):
    decks = Deck.objects.all()
    context = {'decks': decks}
    return render(request, 'flashcards_app/deck_list.html', context)

def deck_detail(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, created_by=request.user)
    flashcards = deck.flashcards.all()
    return render(request, 'flashcards_app/deck_detail.html', {'deck': deck, 'flashcards': flashcards})

def add_deck(request):
    if request.method == 'POST':
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.created_by = request.user
            deck.save()
            return redirect('flashcards:deck_list')
    else:
        form = DeckForm()
    return render(request, 'flashcards_app/add_deck.html', {'form': form})

def add_flashcard(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, created_by=request.user)
    if request.method == 'POST':
        form = FlashcardForm(request.POST)
        if form.is_valid():
            flashcard = form.save(commit=False)
            flashcard.deck = deck
            flashcard.save()
            return redirect('flashcards:deck_detail',deck_id=deck.id)

    else:
        form = FlashcardForm()
    return render(request, 'flashcards_app/add_flashcard.html', {'form': form, 'deck': deck})


def study_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, created_by=request.user)
    flashcards = Flashcard.objects.filter(deck=deck)
    for flashcard in flashcards:
        UserProgress.objects.update_or_create(
            user=request.user,
            flashcard=flashcard,
            defaults={'last_reviewed': timezone.now()}
        )
    return render(request, 'flashcards_app/study_deck.html', {'deck': deck, 'flashcards': flashcards})


cohere_client = cohere.Client('FWkM6KQvBrWjyadYSwEhbKkn5LoedeZr14IZhFbw')

def get_answer_from_cohere(question):
    try:
        # Запрос к Cohere для генерации текста
        response = cohere_client.generate(
            model='command-xlarge-nightly',  # Выбор модели
            prompt=question,  # Текст вопроса
            max_tokens=50,  # Лимит на количество генерируемых токенов
            temperature=0.5  # Температура контролирует креативность (вы можете поэкспериментировать)
        )

        # Извлечение сгенерированного ответа
        if response and response.generations:
            return response.generations[0].text.strip()  # Возвращаем сгенерированный ответ
        return "Ответ отсутствует"

    except cohere.CohereError as e:
        print(f"Ошибка при запросе к API Cohere: {e}")
        return None



# def handle_uploaded_file(f, deck):
#     try:
#         content = f.read().decode('utf-8')
#         lines = content.splitlines()
#         current_question = None
#         answer = ""
#
#         for line in lines:
#             line = line.strip()
#             if '?' in line:
#                 if current_question is not None:
#                     # Сохраняем предыдущий вопрос и ответ
#                     if not answer:  # Если ответа нет, запросить у API
#                         answer = get_answer_from_gemini(current_question)
#                     flashcard = Flashcard(deck=deck, question=current_question, answer=answer)
#                     flashcard.save()
#
#                 current_question = line
#                 answer = ""
#             else:
#                 answer = line  # Сохраняем ответ
#
#         # Сохраняем последний вопрос
#         if current_question is not None:
#             if not answer:  # Если ответ отсутствует
#                 answer = get_answer_from_gemini(current_question)
#             flashcard = Flashcard(deck=deck, question=current_question, answer=answer)
#             flashcard.save()
#
#     except Exception as e:
#         print(f"Произошла ошибка при чтении файла: {e}")

# def handle_uploaded_file(f, deck):
#     try:
#         content = f.read().decode('utf-8')
#         lines = content.splitlines()
#         current_question = None
#         answer = ""
#
#         for line in lines:
#             line = line.strip()
#             if '?' in line:  # Определение вопроса
#                 if current_question is not None:
#                     # Если ответа нет, запросить у API
#                     if not answer:
#                         answer = get_answer_from_gemini(current_question) or "Ответ отсутствует"  # Обработка пустого ответа
#                     flashcard = Flashcard(deck=deck, question=current_question, answer=answer)
#                     flashcard.save()
#
#                 current_question = line
#                 answer = ""
#             else:
#                 answer = line  # Сохранение ответа из файла
#
#         # Сохранение последнего вопроса
#         if current_question is not None:
#             if not answer:  # Если ответ отсутствует
#                 answer = get_answer_from_gemini(current_question) or "Ответ отсутствует"
#             flashcard = Flashcard(deck=deck, question=current_question, answer=answer)
#             flashcard.save()
#
#     except Exception as e:
#         print(f"Произошла ошибка при чтении файла: {e}")


def handle_uploaded_file(f, deck):
    try:
        content = f.read().decode('utf-8')
        lines = content.splitlines()
        current_question = None
        answer = ""

        for line in lines:
            line = line.strip()
            if '?' in line:  # Определение вопроса
                if current_question is not None:
                    # Если ответа нет, запросить у API
                    if not answer:
                        answer = get_answer_from_cohere(current_question) or "Ответ отсутствует"  # Обработка пустого ответа
                    flashcard = Flashcard(deck=deck, question=current_question, answer=answer)
                    flashcard.save()

                current_question = line
                answer = ""
            else:
                answer = line  # Сохранение ответа из файла

        # Сохранение последнего вопроса
        if current_question is not None:
            if not answer:  # Если ответ отсутствует
                answer = get_answer_from_cohere(current_question) or "Ответ отсутствует"
            flashcard = Flashcard(deck=deck, question=current_question, answer=answer)
            flashcard.save()

    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")





def upload_file(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, created_by=request.user)
    error_message = None

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            try:
                handle_uploaded_file(uploaded_file, deck)
                return redirect('flashcards:deck_detail', deck_id=deck.id)
            except Exception as e:
                error_message = f"Ошибка загрузки файла: {e}"
    else:
        form = UploadFileForm()

    return render(request, 'flashcards_app/upload_file.html', {'form': form, 'deck': deck, 'error_message': error_message})



from django.contrib import messages



def delete_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id)

    if request.method == 'POST':
        deck.delete()
        messages.success(request, "Колода успешно удалена!")


    messages.error(request, 'Запрос на удаление не был выполнен')
    return redirect('flashcards:deck_list')

