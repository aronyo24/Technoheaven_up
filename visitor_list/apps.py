from django.apps import AppConfig


class VisitorListConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visitor_list'
    

    def ready(self):
        import visitor_list.middleware