from ore.viewlet import core
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zc.table import table, column

from Products.CMFPlone.i18nl10n import utranslate
from Products.PloneGetPaid.i18n import _

from Products.PloneGetPaid.browser.admin_order import BatchingFormatter

from Products.PloneGetPaid.browser.admin_order import renderOrderId, AttrColumn, DateColumn, PriceColumn, renderItemId, renderItemName, renderItemCost, renderItemPrice
from Products.PloneGetPaid.browser.admin_order import OrderListingComponent as BaseOrderListingComponent
from Products.PloneGetPaid.browser.admin_order import OrderContentsComponent as BaseOrderContentsComponent

def raw_cell_formatter(value, item, formatter):
    return unicode(value)

class OrderListingComponent( BaseOrderListingComponent ):

#    template = ZopeTwoPageTemplateFile('templates/orders-listing.pt')
    
    columns = [
        column.GetterColumn( title=_(u"Order Id"), getter=renderOrderId, cell_formatter=raw_cell_formatter ),
        column.GetterColumn( title=_(u"Customer Id"), getter=AttrColumn("user_id" ) ), 
#        column.GetterColumn( title=_(u"Last4"), getter=AttrColumn("user_payment_info_last4" ) ),
#        column.GetterColumn( title=_(u"Proc Trans Id"), getter=AttrColumn("user_payment_info_trans_id" ) ),       
#        column.GetterColumn( title=_(u"Name on Card"), getter=AttrColumn("name_on_card" ) ),       
#        column.GetterColumn( title=_(u"Card Phone#"), getter=AttrColumn("bill_phone_number" ) ),       
        column.GetterColumn( title=_(u"Status"), getter=AttrColumn("finance_state") ),
#        column.GetterColumn( title=_(u"Fulfillment"), getter=AttrColumn("fulfillment_state") ),
        column.GetterColumn( title=_(u"Price"), getter=PriceColumn("getTotalPrice") ),
        column.GetterColumn( title=_(u"Created"), getter=DateColumn("creation_date") )
        ]

    
class OrderContentsComponent( BaseOrderContentsComponent ):
    """ an item listing used to group items by workflow state and present
    relevant workflow actions """

#    interface.implements( )
    
#    template = ZopeTwoPageTemplateFile('templates/order-item-listing.pt')
    
    columns = [
        column.SelectionColumn( lambda item: item.item_id, name="selection"),
        column.GetterColumn( title=_(u"Quantity"), getter=AttrColumn("quantity" ) ),
        column.GetterColumn( title=_(u"Item Id"), getter=renderItemId, cell_formatter=raw_cell_formatter ),
        column.GetterColumn( title=_(u"Name"), getter=renderItemName, cell_formatter=raw_cell_formatter ),
        column.GetterColumn( title=_(u"Price"), getter=renderItemCost ),        
#        column.GetterColumn( title=_(u"Total"), getter=renderItemPrice ),        
#        column.GetterColumn( title=_(u"Status"), getter=AttrColumn("fulfillment_state" ) ),
        ]

# for use when we're still reviewing workflow state
class AllItems( OrderContentsComponent ):

    actions = form.Actions()

    columns = list( OrderContentsComponent.columns )
#    columns.remove( OrderContentsComponent.selection_column )

    def update( self ):
        self.line_items = self.__parent__.context.shopping_cart.values()
        return super( OrderContentsComponent, self).update()
