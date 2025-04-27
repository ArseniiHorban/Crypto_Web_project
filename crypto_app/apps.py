from django.apps import AppConfig

class CustomAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crypto_app'

    def ready(self):
        # Start the background task for fetching coin data
        import crypto_app.tasks
