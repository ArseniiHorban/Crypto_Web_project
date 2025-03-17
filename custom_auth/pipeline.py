import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def check_existing_user_by_email(backend, details, response, *args, **kwargs):
    """
    Проверяем, существует ли пользователь с таким email.
    Если да, возвращаем его и пропускаем создание нового пользователя.
    """
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
            return None
    logger.info("check_existing_user_by_email: No email provided")
    return None