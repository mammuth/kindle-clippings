from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


@apphook_pool.register
class ClippingManagerApphook(CMSApp):
    app_name = "clipping_manager"
    name = _("Clipping Manager Application")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["clipping_manager.urls"]