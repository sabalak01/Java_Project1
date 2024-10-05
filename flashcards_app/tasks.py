from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User


@shared_task
def send_notification(user_id):
    try:
        user = User.objects.get(id=user_id)
        subject = 'Time to Study Your Flashcards!'
        message = f'Hi {user.username},\n\nIt\'s time to review your flashcards. Keep up the good work!\n\nBest,\nFlashcard Learning App'.format(
            user.username)
        from_email = 'flashcards007@gmail.com'

        # Отправка уведомления
        send_mail(subject, message, from_email, [user.email])
    except User.DoesNotExist:
        print(f'User with id {user_id} does not exist.')
    except Exception as e:
        print(f'An error occurred: {e}')
