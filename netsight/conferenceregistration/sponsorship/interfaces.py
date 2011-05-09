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


class SimpleVocabulary(vocabulary.SimpleVocabulary):

    def __init__(self, context):
        registry = getUtility(IRegistry)
        levels = [
            tuple(level.split(',')) for level in
            registry[ISponsorshipSettings.__identifier__+'.levels']]
        self.max_by_idx = max_by_idx = dict(
            (idx, int(level[2])) for idx, level in enumerate(levels)
            if len(level) == 3)

        self.counts = counts = {}
        for sponsor in context.contentValues(dict(
            portal_type='netsight.conferenceregistration.sponsor')):
            level = sponsor.level
            if level in max_by_idx:
                count = counts.get(level, 0) + 1
                counts[level] = count

        super(SimpleVocabulary, self).__init__([
            vocabulary.SimpleTerm(idx, title=u'%s - $%s' % level[:2])
            for idx, level in enumerate(levels)])

    def __iter__(self):
        """Skip levels whose max has been reached."""
        for idx, term in enumerate(
            super(SimpleVocabulary, self).__iter__()):
            if (idx not in self.max_by_idx or
                self.counts.get(idx, 0) < self.max_by_idx[idx]):
                yield term
            

class LevelsSourceBinder(object):
    interface.implements(interfaces.IContextSourceBinder)

    def __call__(self, context):
        return SimpleVocabulary(context)


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
