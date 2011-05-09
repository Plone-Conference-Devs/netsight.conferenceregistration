from zope.interface import Interface
from zope import interface
from zope import schema
from zope.schema import interfaces
from zope.schema import vocabulary
from zope.component import getUtility

from z3c.form.browser import select

from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile import field
from plone.registry.interfaces import IRegistry
from plone.registry import field as reg_field


class LevelsSourceBinder(object):
    interface.implements(interfaces.IContextSourceBinder)

    def __call__(self, context):
        registry = getUtility(IRegistry)
        levels = registry[ISponsorshipSettings.__identifier__+'.levels']
        return vocabulary.SimpleVocabulary([
            vocabulary.SimpleTerm(
                idx, title=level.split(',', 1)[0].strip())
            for idx, level in enumerate(levels)])


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
        value_type=reg_field.TextLine(
            # TODO schema=ISponsorshipLevel,
            title=u'Sponsorship Level',
            description=u'Name,amount,max'))


def PromptSelectFieldWidget(field, request):
    widget = select.SelectWidget(request)
    widget.prompt = True
    widget.promptMessage = u'Please select a sponsorship level ...'
    return select.FieldWidget(field, widget)


class ISponsor(form.Schema):

    title = schema.TextLine(
        title=u'Name')

    form.widget(level=PromptSelectFieldWidget)
    level = schema.Choice(
        title=u'Sponsorship Level',
        source=LevelsSourceBinder())

    text = RichText(
        title=u'Body Text')
    image = field.NamedBlobImage(
        title=u'Image')
