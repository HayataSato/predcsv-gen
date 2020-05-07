from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("predictor.urls")),
    path('sw.js', (TemplateView.as_view(template_name="predictor/sw.js", content_type='application/javascript', )), name='sw.js'),
    path('select2/', include('django_select2.urls')),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)