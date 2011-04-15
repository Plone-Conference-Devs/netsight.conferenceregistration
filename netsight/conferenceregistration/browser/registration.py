from five import grok
from plone.directives import form

from zope import schema
from z3c.form import button, field, group
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.form import applyChanges

from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage

from netsight.conferenceregistration import _
from netsight.conferenceregistration.attendee import IAttendee

from plone.dexterity.utils import createContentInContainer

from plone.supermodel.model import Fieldset
from plone.supermodel.interfaces import FIELDSETS_KEY

from zope import interface, component
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

from zope.app.intid.interfaces import IIntIds
from getpaid.core import interfaces, item

from Products.PloneGetPaid.interfaces import IPayableMarker
from Products.Five.utilities.marker import mark
from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from netsight.conferenceregistration.interfaces import IRegistrationFolder

from netsight.conferenceregistration.discounts import DISCOUNTS

class ContactGroup(group.Group):
    label=u"Contact Details"
    description=u"Enter your contact details below"
    fields=field.Fields(IAttendee).select(
        'firstname', 'lastname', 'city', 'postcode', 'country', 'email',
        )

class TicketGroup(group.Group):
    label=u"Ticket Type"
    description=u"Please enter any discount code you have been given. If you are a speaker, enter the code 'speaker'"
    fields=field.Fields(IAttendee).select(
#        'ticket',
        'discount_code',
        )

class PreferencesGroup(group.Group):
    label=u"Preferences"
    description=u"Let us know of any dietry requirements you have, t-shirt size and if you will be attending the sprints"
    fields=field.Fields(IAttendee).select(
        'food', 'food_other', 'shirt', 'sprints',
        )

class BadgeGroup(group.Group):
    label=u"Badge Details"
    description=u"The details below will appear on your delegates badge"
    fields=field.Fields(IAttendee).select(
        'badge_name', 'badge_line1', 'badge_line2', 'badge_url', 
        'badge_email', 'badge_nickname',
        )

class PrivacyGroup(group.Group):
    label=u"Privacy and Mailings"
    description=u""
    fields=field.Fields(IAttendee).select(
        'badge_public', 'mailing_list', 'pf_mailings',
        )
    

class RegistrationForm(group.GroupForm, form.Form):
    grok.name('registration')
    grok.require('zope2.View')
    grok.context(IRegistrationFolder)

    fields=field.Fields(IAttendee).select('uid')
    
    groups = (ContactGroup, TicketGroup, PreferencesGroup, BadgeGroup, PrivacyGroup)

    template = ViewPageTemplateFile('templates/registration_form.pt')

    label = _(u"Register for Plone Conference 2010")

    enable_form_tabbing = False

    def update(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)
        content = self.getContent()
        if content is not None:
            self.groups = [ g(content, self.request, self) for g in self.groups ]
        else:
            self.ignoreContext = True

        # call the base class version - this is very important!
        super(RegistrationForm, self).update()

    def updateWidgets(self):
        super(RegistrationForm, self).updateWidgets()
        self.widgets['uid'].mode = HIDDEN_MODE


    def getContent(self):

        key = self.request.form.get('key')
        if not key:
            try:
                data, errors = self.extractData(setErrors=False)
                key = data.get('uid')
            except AttributeError:
                pass

        if key:
            try:
                key = int(key)
            except ValueError:
                return

            return self.getattendee(key)

    def getattendee(self, uid):
        intids = component.getUtility(IIntIds)
        wf = getToolByName(self.context, 'portal_workflow')
        for attendee in self.context.attendees.contentValues():
            if intids.getId(attendee) == uid:
                # XXX add check for workflow state == unpa
                if wf.getStatusOf("attendee_workflow", attendee)["review_state"] == 'unpaid':
                    return attendee

    @button.buttonAndHandler(_(u'Register'))
    def handleApply(self, action):


        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        uid = data.get('uid')
        if uid: # this is an existing registration
            attendee = self.getattendee(uid)
            if attendee is None:
                # we should not get here... tampering alert
                raise ValueError, "Tampering with the form!"
            
            for group in self.groups:
                changes = applyChanges(group, attendee, data)

        else:
            # Create the attendee object in the attendees folder
            attendees = self.context.attendees
            del data['uid'] # need to remove uid before adding
            attendee = createContentInContainer(attendees, 'netsight.conferenceregistration.attendee', 
                                                checkConstraints=False, **data)

        # Add attendee to shopping cart

        self.addToCart(attendee)

#        IStatusMessage(self.request).addStatusMessage(
#                _(u"Thank you for your registration."), 
#                "info"
#            )

        portal_url = getToolByName( self.context, 'portal_url').getPortalObject().absolute_url()
        return self.request.response.redirect('%s/register/@@getpaid-cart' % portal_url)    
        

    def addToCart(self, attendee):
        utility = component.getUtility( interfaces.IShoppingCartUtility )
        cart = utility.get(self.context, create=True)
                
        # get the price for the posting
        price =  DISCOUNTS.get(attendee.discount_code, 320)

        #code was not in svn
#        if attendee.ticket == 'speaker':
#            price = 150
#        else:
#            price = 320
        #elif attendee.ticket == 'test':
        #    price = 20
    
        #code in svn
        #price = 250
        #price = 320


        intids = component.getUtility( IIntIds )
        iid = intids.queryId( attendee )
        if iid is None:
            iid = intids.register( attendee )

        nitem = item.PayableLineItem()
        nitem.item_id = str(iid) # archetypes uid
        nitem.uid = iid

        # Already in there, remove the old one
        if nitem.item_id in cart:
            del cart[nitem.item_id]

        # copy over information regarding the item
#        ticket_vocab = queryUtility(IVocabularyFactory, name='netsight.conferenceregistration.tickets')(self.context)
#        ticket = ticket_vocab.getTerm(attendee.ticket).token

        if attendee.discount_code:
            nitem.name = "Plone Conference 2010 ticket (%s) - %s" % (attendee.discount_code, attendee.Title())
        else:
            nitem.name = "Plone Conference 2010 ticket - %s" % attendee.Title()
        nitem.description = nitem.name # description
        nitem.cost = price
        nitem.quantity = 1
        nitem.product_code = nitem.item_id
        
        # add to cart
        cart[ nitem.item_id ] = nitem
        cart.last_item = nitem.item_id        

        # send email with details to get registration back
        if price != 0:
            from netsight.conferenceregistration.browser.email import email
            email(attendee, self.context).sendemail()

        print "Added!", nitem.item_id
