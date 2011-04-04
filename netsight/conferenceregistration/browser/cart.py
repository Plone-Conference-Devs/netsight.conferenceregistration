from zope.formlib import form
from zc.table import column, table

from zope import schema, component

from ore.viewlet.container import ContainerViewlet
from ore.viewlet.core import FormViewlet
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName

from getpaid.core import interfaces

from Products.PloneGetPaid import sessions
from Products.PloneGetPaid.i18n import _
#from Products.PloneGetPaid.browser.cart import CartFormatter
from Products.PloneGetPaid.browser.cart import lineItemPrice, lineItemTotal

from Products.CMFPlone.i18nl10n import utranslate
from Products.CMFPlone.utils import safe_unicode


class ShoppingCartActions( FormViewlet ):

    template = ZopeTwoPageTemplateFile('templates/cart-actions.pt')

    def render( self ):
        return self.template()

    def doesCartContainItems( self, *args ):
        return bool(  len( self.__parent__.cart ) )

    def isLoggedIn( self, *args ):
        return getSecurityManager().getUser().getId() is not None

    def isAnonymous( self, *args ):
        return getSecurityManager().getUser().getId() is None

    @form.action(_("Register another person"), name='continue-shopping')
    def handle_continue_shopping( self, action, data ):
        # Go back to the registration form
        portal = getToolByName( self.context, 'portal_url').getPortalObject()
        url = portal.absolute_url() + '/register'
        return self.request.RESPONSE.redirect( url )

    @form.action(_("Checkout and Pay for Registrations"), condition="doesCartContainItems", name="Checkout")
    def handle_checkout( self, action, data ):
        # go to order-create
        # force ssl? redirect host? options
        portal = getToolByName( self.context, 'portal_url').getPortalObject()
        url = portal.absolute_url() + '/register/@@getpaid-checkout-wizard#content'
        return self.request.RESPONSE.redirect( url )


class CartFormatter( table.StandaloneSortFormatter ):

    def getTotals( self ):
        #if interfaces.IShoppingCart.providedBy( self.context ):
        return interfaces.ILineContainerTotals( self.context )
        
    def renderExtra( self ):

        translate = lambda msg: utranslate(domain='plonegetpaid',
                                           msgid=msg,
                                           context=self.request)

        if not len( self.context ):
            return super( CartFormatter, self).renderExtra()
        
        totals = self.getTotals()

        tax_list = totals.getTaxCost()
        shipping_price = totals.getShippingCost()
        subtotal_price = totals.getSubTotalPrice()
        total_price = totals.getTotalPrice()
        
        buffer = [ u'<div class="getpaid-totals"><table class="listing">']
        buffer.append('<tr><th>')
        buffer.append( translate(_(u"SubTotal")) )
        buffer.append( '</th><td style="border-top:1px solid #8CACBB;">%0.2f</td></tr>'%( subtotal_price ) )

#        buffer.append( "<tr><th>" )
#        buffer.append( translate(_(u"Shipping")) )
#        buffer.append( "</th><td>%0.2f</td></tr>"%( shipping_price ) )

        for tax in tax_list:
            buffer.append( "<tr><th>%s</th><td>%0.2f</td></tr>"%( tax['name'], tax['value'] ) )
        buffer.append( "<tr><th>" )
        buffer.append( translate(_(u"Total")) )
        buffer.append( "</th><td>%0.2f</td></tr>"%( total_price ) )
        buffer.append('</table></div>')
        
        return u''.join( buffer) + super( CartFormatter, self).renderExtra()

def lineItemURL( item, formatter ):
    return '%s'  % safe_unicode(item.name)

class ShoppingCartListing( ContainerViewlet ):

    actions = ContainerViewlet.actions.copy()

    columns = [
        column.SelectionColumn( lambda item: item.item_id, name="selection"),
        column.GetterColumn( title=_(u"Name"), getter=lineItemURL ),
        column.GetterColumn( title=_(u"Price"), getter=lineItemPrice ),
       ]

    selection_column = columns[0]
    template = ZopeTwoPageTemplateFile('templates/cart-listing.pt')

    formatter_factory = CartFormatter
    
    def __init__( self, *args, **kw):
        super( ShoppingCartListing, self ).__init__( *args, **kw )

        for column in self.columns:
            if hasattr(column, 'title'):
                column.title = utranslate(domain='plonegetpaid',
                                          msgid=column.title,
                                          context=self.request)

    def getContainerContext( self ):
        return self.__parent__.cart

    def isOrdered( self, *args ):
        # shopping cart should not be ordered, so override this with False
        return False
    

