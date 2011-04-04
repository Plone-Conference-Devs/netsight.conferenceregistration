from Products.Five import BrowserView


class email(BrowserView):

    def __call__(self):
        return self.sendemail()

    def sendemail(self):
        # Try and send them an email about the registration
        from random import randint
        import os.path
        import smtplib

        attendee = self.context

        try:
            directory, _f = os.path.split(os.path.abspath(__file__))
            template = os.path.join(directory, 'regemail1.txt')
            template = unicode(open(template).read())

            id = "%04d-%04d-%04d" % (randint(0,9999), randint(0,9999), randint(0,9999))
            msg = template % dict(id=id, 
                                  firstname=attendee.firstname, 
                                  key=attendee.uid,
                                  email=attendee.email, 
                                  )
            msg = msg.encode('utf-8')

            fromaddr = 'info@ploneconf2010.org'
            toaddrs = [attendee.email, 'info@ploneconf2010.org',]

            server = smtplib.SMTP('mail.netsight.co.uk')
            server.set_debuglevel(1)

            server.sendmail(fromaddr, toaddrs, msg)
            server.quit()

            return "email sent"

        except:
            print "Count not send mail to: %s" % attendee.email
            return "Count not send mail to: %s" % attendee.email
