from django.contrib import admin


# La administracion de los modelos contables base se registra en apps.core.admin.
# Este modulo queda reservado para modelos contables adicionales propios de
# apps.contabilidad, evitando imports rotos durante autodiscover().
