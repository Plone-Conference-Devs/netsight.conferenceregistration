from Products.Five import BrowserView
import logging
from random import randint
import os.path
import smtplib
from Products.CMFCore.utils import getToolByName
from netsight.conferenceregistration import regutils


class email(BrowserView):

    def __call__(self):
        return self.sendemail()

    def sendemail(self):
        """ Send confirmation email about registration """
        attendee = self.context

        try:
            directory, _f = os.path.split(os.path.abspath(__file__))
            template = os.path.join(directory, 'regemail1.txt')
            template = unicode(open(template).read())

            id = "%04d-%04d-%04d" % (randint(0,9999), randint(0,9999), randint(0,9999))
            msg = template % dict(id=id, 
                                  firstname=attendee.firstname, 
                                  key=attendee.getId(),
                                  email=attendee.email, 
                                  year=regutils.getConferenceYear(),
                                  )
            msg = msg.encode('utf-8')

            fromaddr = 'info@ploneconf.org'
            toaddrs = [attendee.email, fromaddr,]
            
            mh = getToolByName(self.context, 'MailHost')
            mh.send(msg, mto=toaddrs, mfrom=fromaddr, 
                    encode='utf8', charset='utf8')
            
            return True

        except Exception, e:
            logging.error( "Count not send mail to: %s : %s" % (attendee.email, e))
        
        return False
