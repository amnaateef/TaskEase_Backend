from django.apps import AppConfig


class UserSignupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_signup'

    def ready(self):
        import user_signup.models  # noqa
