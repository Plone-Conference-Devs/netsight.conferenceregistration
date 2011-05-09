from five import grok
from zope.schema import TextLine, Choice, Bool, Int

from plone.directives import form

from netsight.conferenceregistration import _
from netsight.conferenceregistration.validators import isEmail

from plone.dexterity.content import Item

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

class Attendee(Item):
    """ An attendee """

    def Title(self):
        """ return the title """
        return INameFromTitle(self).title

    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)

class IAttendee(form.Schema):
    """A conference attendee"""

    ### Contact details

    uid = Int(
        title=_(u"uid"),
        required=False,
        )

    firstname = TextLine(
        title=_(u"First Name"),
        )

    lastname = TextLine(
        title=_(u"Last Name"),
        )

    city = TextLine(
        title=u'City',
        required=True,
        )

    postcode = TextLine(
        title=u'Post Code / Zip Code',
        required=True,
        )

    country = Choice(
        title=u'Country',
        required=True,
        vocabulary="netsight.conferenceregistration.countries"
        )

    email = TextLine(
        title =_(u"Email address"),
        )

    ### Ticket type


    price_id = Choice(
        title=u'Ticket type',
        description = u'Ticket prices include service fees.',
        required=True,
        vocabulary="netsight.conferenceregistration.prices",
        )

    ### Preferences

    food = Choice(
        title=u'Food preferences',
        required=True,
        vocabulary="netsight.conferenceregistration.food"
        )

    food_other = TextLine(
        title=u'Other food preference (if other is specified above)',
        required=False,
        )

    shirt = Choice(
        title=u'Conference T-Shirt size',
        required=True,
        vocabulary="netsight.conferenceregistration.shirts"
        )

    sprints = Choice(
        title=u'Sprints',
        description=u"Will you be attending the developer sprints afterwards (this is not final, it's just so we have a rough idea of numbers)",
        vocabulary="netsight.conferenceregistration.sprints"
        )


    ### Badge details

    badge_name = TextLine(
        title=u'Name',
        description=u'The Name that should be printed on the badge',
        required=True,
        missing_value=u'',
        )

    badge_line1 = TextLine(
        title=u'Company name, "Freelancer" or any other information ' +\
              u'you like to have printed below the name',
        required=False,
        missing_value=u'',
        )

    badge_line2 = TextLine(
        title=u'Second line printed below the Name',
        required=False,
        missing_value=u'',
        )

    badge_url = TextLine(
        title=u'Website',
        required=False,
        missing_value=u'',
#        constraint=isHttpURL,
        )

    badge_email = TextLine(
        title=u'E-Mail Address',
        required=False,
        missing_value=u'',
        constraint=isEmail,
        )

    badge_nickname = TextLine(
        title=u'IRC Nickname',
        required=False,
        missing_value=u'',
        )

    badge_public = Bool(
        title=u'Show the badge information in the delegate list',
        description=u'Clear this box if you do not want your badge information to be displayed on the website prior to the conference',
        required=True,
        default=True,
        )

    badge_type = Choice(
        title=u'Badge Type',
        required=False,
        vocabulary="netsight.conferenceregistration.badgetypes"
        )

    mailing_list = Bool(
        title=u'Add me to the Plone Conference mailing list',
        description=u'This will be a low volume mailout with updates and information prior to the conference',
        required=True,
        default=True,
        )

    pf_mailings = Bool(
        title=u'Allow the Plone Foundation to contact me about future Plone events',
        description=u'The Plone Foundation would like to periodically let you know about '\
                    u'other Plone conferences or events happening around the year. '\
                    u'If you wish to not receive these mailings, please uncheck this box.',
        required=True,
        default=True,
        )

from plone.app.content.interfaces import INameFromTitle

class TitleAdapter(grok.Adapter):
    grok.provides(INameFromTitle)
    grok.context(IAttendee)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        return '%s, %s' % (self.context.lastname, self.context.firstname)



