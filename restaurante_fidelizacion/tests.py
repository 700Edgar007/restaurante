import importlib
import tempfile

from django.test import SimpleTestCase, override_settings
from django.urls import clear_url_caches


class LocalMediaUrlsTests(SimpleTestCase):
    @override_settings(DEBUG=False, MEDIA_URL='/media/', MEDIA_ROOT=tempfile.gettempdir())
    def test_media_urls_siguen_disponibles_con_storage_local_en_produccion(self):
        from restaurante_fidelizacion import urls as project_urls

        clear_url_caches()
        importlib.reload(project_urls)

        try:
            media_patterns = [
                pattern for pattern in project_urls.urlpatterns
                if getattr(getattr(pattern, 'pattern', None), 'regex', None)
                and pattern.pattern.regex.pattern.startswith('^media/')
            ]
        finally:
            clear_url_caches()
            importlib.reload(project_urls)

        self.assertTrue(media_patterns)
