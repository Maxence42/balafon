# -*- coding: utf-8 -*-
"""a simple store"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from coop_cms.utils import dehtml

from balafon.utils import logger
from balafon.Store.settings import get_cart_confirmation_subject


def notify_cart_to_admin(profile, action):
    """send message by email"""
    notification_email = getattr(settings, 'BALAFON_NOTIFICATION_EMAIL', '')
    if notification_email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        subject = _(u"New cart purchased on store")
        data = {
            'profile': profile,
            'action': action,
            'subject': subject,
        }
        the_template = get_template('Store/cart_notification_email.html')
        html_text = the_template.render(Context(data))
        text = dehtml(html_text)

        email = EmailMultiAlternatives(
            subject,
            text,
            from_email,
            [notification_email],
            headers={'Reply-To': profile.contact.email}
        )
        email.attach_alternative(html_text, "text/html")

        try:
            email.send()
        except Exception:
            logger.exception("notify_cart_to_admin")


def confirm_cart_to_user(profile, action):
    """send message by email"""

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
    subject = get_cart_confirmation_subject()


    data = {
        'profile': profile,
        'action': action,
        'subject': subject,
    }


    the_template = get_template('Store/cart_confirmation_email.html')
    html_text = the_template.render(Context(data))
    text = dehtml(html_text)

    email = EmailMultiAlternatives(
        subject,
        text,
        from_email,
        [profile.contact.email],
    )
    email.attach_alternative(html_text, "text/html")

    try:
        email.send()
    except Exception:
        logger.exception("confirm_cart_to_user")
