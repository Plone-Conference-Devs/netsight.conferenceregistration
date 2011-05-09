import re
import zope
from discounts import DISCOUNTS

EMAIL_RE = "^([0-9a-zA-Z_&.+-]+!)*[0-9a-zA-Z_&.+-]+@(([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-z-A-Z])?\.)+[a-zA-Z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$"
mailre = re.compile(EMAIL_RE)

class EMailException(zope.schema.ValidationError):
    __doc__ = u"Please use a valid email address like info@ploneconf.org"
    zope.interface.implements(zope.app.form.interfaces.IWidgetInputError)

class UrlException(zope.schema.ValidationError):
    __doc__ = u"""Please use a valid url like http://ploneconf.org"""
    zope.interface.implements(zope.app.form.interfaces.IWidgetInputError)

class DiscountException(zope.schema.ValidationError):
    __doc__ = u"""That is not a valid discount code"""
    zope.interface.implements(zope.app.form.interfaces.IWidgetInputError)


def isEmail(value):
    #borrowed from validation.validators.Basevalidators                                                                                                       
    if mailre.match(value):
        return True
    else:
        raise EMailException


def isHttpURL(value):
    if value.startswith('http://') or \
       value.startswith('https://'):
        return True
    else:
        raise UrlException

def isDiscount(value):
    if not value:
        return True
    if value in DISCOUNTS:
        return True
    else:
        raise DiscountException
        
