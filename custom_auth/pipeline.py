import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def check_existing_user_by_email(backend, details, response, *args, **kwargs):
    """
    Проверяем, существует ли пользователь с таким email.
    Если да, возвращаем его и пропускаем создание нового пользователя.
    """

    logger.info(f"check_existing_user_by_email: Received details: {details}")
    logger.info(f"check_existing_user_by_email: Received response: {response}")
    email = details.get('email')
    logger.info(f"check_existing_user_by_email: Checking email: {email}")
    if email:
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            logger.info(f"check_existing_user_by_email: Found user with email: {email}")
            return {
                'user': user,
                'is_new': False
            }
        except User.DoesNotExist:
            logger.info(f"check_existing_user_by_email: No user found with email: {email}")
            # Генерируем username на основе имени из Google
            name = details.get('name', email.split('@')[0])  # Используем name или часть email
            username = name.lower().replace(' ', '_')[:30]  # Усекаем до 30 символов
            # Убеждаемся, что username уникален
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            logger.info(f"check_existing_user_by_email: Creating new user with username: {username}")
            return {
                'user': User.objects.create_user(username=username, email=email, password=None),
                'is_new': True
            }
    logger.info("check_existing_user_by_email: No email provided")
    return None