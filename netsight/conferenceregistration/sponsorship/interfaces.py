from zope.interface import Interface
from zope import schema

from plone.registry import field


class ISponsorshipLevel(Interface):

    name = schema.TextLine(
        title=u'Name')
    amount = schema.Int(
        title=u'Amount')
    maximum = schema.Int(
        title=u'Number Allowed')    
    

class ISponsorshipSettings(Interface):

    levels = schema.Tuple(
        title=u'Sponsorship Levels',
        value_type=field.TextLine(
            # TODO schema=ISponsorshipLevel,
            title=u'Sponsorship Level',
            description=u'Name,amount,max'))
            
