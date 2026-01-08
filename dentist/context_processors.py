"""
Sayt sozlamalarini barcha sahifalarga uzatuvchi context processor
"""

from dentist.models import SiteSettings


def site_settings(request):
    """Barcha template'larga site_settings ni qo'shadi"""
    return {
        'site_settings': SiteSettings.get_settings()
    }
