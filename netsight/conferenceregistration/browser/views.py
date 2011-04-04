from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName 
from zope.component import getUtility
from getpaid.core.interfaces import IOrderManager

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from StringIO import StringIO
from pyPdf import PdfFileReader, PdfFileWriter

import os.path

class mailinglist(BrowserView):

    def emails(self):
        attendees = self.context.contentValues()
        emails = [ x.email for x in attendees if x.mailing_list ]
        return emails
#        emails = [ x.email for x in attendees ]
        return list(set(emails))


class registrations(BrowserView):

    def registrations(self):
        regs = []
        wf = getToolByName(self.context, 'portal_workflow')
        manager = getUtility( IOrderManager )

        order2attendee = {}

        orders = manager.storage.values()
        for o in orders:
            order_id = o.order_id
            for ticket in o.shopping_cart.values():
                attendee = ticket.resolve()
                order2attendee[attendee] = order_id

        for attendee in self.context.contentValues():
            regs.append({'uid': attendee.uid,
                         'firstname': attendee.firstname,
                         'lastname': attendee.lastname,
                         'country': attendee.country,
                         'status': wf.getStatusOf("attendee_workflow", attendee)["review_state"],
                         'url': attendee.absolute_url(),
                         'order_id': order2attendee.get(attendee, '')
                         }
                        )
        return regs

class food(BrowserView):

    def food(self):
        food = {}
        wf = getToolByName(self.context, 'portal_workflow')
        attendees = self.context.contentValues()
        for attendee in attendees:
            if wf.getStatusOf("attendee_workflow", attendee)["review_state"] == 'unpaid':
                continue
            if attendee.food == 'other':
                food[attendee.food_other] = food.get(attendee.food_other, 0) + 1
            else:
                food[attendee.food] = food.get(attendee.food, 0) + 1

        food = food.items()
        return food


class shirts(BrowserView):

    def shirts(self):

        shirts = {}
        attendees = self.context.contentValues()
        for attendee in attendees:
            shirts[attendee.shirt] = shirts.get(attendee.shirt, 0) + 1


        total = len(attendees)
        shirts = shirts.items()
        shirts.sort()
        shirts = [ (dict(size=size,actual=num,guess=int(num*(300.0/total)))) for size,num in shirts ]
        return shirts

    def total(self):
        return len(self.context.contentValues())
            

class sprints(BrowserView):

    def __call__(self):
        res = ""
        attendees = self.context.contentValues()
        for a in attendees:
            res += a.country + "\n"
        return res
#        return len([x for x in attendees if x.sprints == 'one' or x.sprints == 'two'])


class badges(BrowserView):


#    name = "Iain Claridge"
#    company = "Netsight Internet Solutions"
#    nextline = "Lead Designer"
#    ircname = "BlackTurtleNeck"
#    country = "UK"
#    foodpref = ""
#    tshirt = "Large"

    def __call__(self):
        directory, _f = os.path.split(os.path.abspath(__file__))
        badge_silver = os.path.join(directory, 'badge_silver.pdf')
        badge_gold = os.path.join(directory, 'badge_gold.pdf')
        badge_bronze = os.path.join(directory, 'badge_bronze.pdf')
        badge_supporting = os.path.join(directory, 'badge_blue.pdf')
        badge_normal = os.path.join(directory, 'badge_blue.pdf')
        badge_staff = os.path.join(directory, 'badge_blue.pdf')

        out = PdfFileWriter()
        
        badgebases = { 'Silver Sponsor': open(badge_silver, 'r'),
                       'Gold Sponsor': open(badge_gold, 'r'),
                       'Bronze Sponsor': open(badge_bronze, 'r'),
                       'Supporting Sponsor': open(badge_supporting, 'r'),
                       'Staff': open(badge_staff, 'r'),
                       'Normal': open(badge_normal, 'r'),
                       }

        attendees = self.context.contentValues()
        for attendee in sorted(attendees, key=lambda x: x.lastname)[:5]:

            name = attendee.badge_name
            company = attendee.badge_line1
            nextline = attendee.badge_line2
            ircname = attendee.badge_nickname
            country = attendee.country
            foodpref = attendee.food
            if foodpref == 'Other':
                foodpref = attendee.food_other
            tshirt = attendee.shirt

            text = StringIO()
            
            c = canvas.Canvas(text, pagesize=(8*cm, 15*cm))
            c.setStrokeColorRGB(0,0,0)

            fontsize = 30
            while c.stringWidth(name,"Helvetica-Bold", fontsize) > 7.5*cm:
                fontsize -= 6

            c.setFont("Helvetica-Bold", fontsize)
            c.drawCentredString(8*cm/2, 8.2*cm, name)
            
            fontsize = 14
            while c.stringWidth(company,"Helvetica-Bold", fontsize) > 7.5*cm:
                fontsize -= 6
            c.setFont("Helvetica-Bold", fontsize)
            c.drawCentredString(8*cm/2, 7.2*cm, company)

            fontsize = 14
            while c.stringWidth(nextline,"Helvetica-Bold", fontsize) > 7.5*cm:
                fontsize -= 6
            c.setFont("Helvetica-Bold", fontsize)
            c.drawCentredString(8*cm/2, 6.5*cm, nextline)

            fontsize = 14
            while c.stringWidth(ircname,"Helvetica-BoldOblique", fontsize) > 7.5*cm:
                fontsize -= 6
            c.setFont("Helvetica-BoldOblique", fontsize)
            c.drawCentredString(8*cm/2, 5.6*cm, ircname)

            fontsize = 14
            while c.stringWidth(country,"Helvetica-Bold", fontsize) > 7.5*cm:
                fontsize -= 6
            c.setFont("Helvetica-Bold", fontsize)
            c.drawCentredString(8*cm/2, 4.7*cm, country)

            c.saveState()
            c.rotate(180)
            c.setFont("Helvetica", 10)
            c.drawCentredString(-8*cm/2, -0.8*cm, "food: %s" % foodpref)
            c.drawCentredString(-8*cm/2, -1.3*cm, "t-shirt: %s" % tshirt)
            c.restoreState()

            c.showPage()

            c.save()

            text.seek(0)

            text = PdfFileReader(text)
            textpage = text.getPage(0)
            badgetype = attendee.badge_type
            if not badgetype:
                badgetype = 'Normal'
            badgebase = badgebases[badgetype]
            badgebase.seek(0)
            base = PdfFileReader(badgebase)
            basepage = base.getPage(0)
        
            basepage.mergePage(textpage)

            out.addPage(basepage)

        result = StringIO()
        out.write(result)

        cd = 'attachment; filename=badges.pdf'
        self.request.response.setHeader("Content-Disposition", cd)
        self.request.response.setHeader("Content-Type", 'application/pdf')

        return result.getvalue()
