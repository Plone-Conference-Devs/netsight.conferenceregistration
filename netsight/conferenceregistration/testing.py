from plone.app import testing

from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName


class ConferenceFixture(testing.PloneSandboxLayer):
    default_bases = (testing.PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import netsight.conferenceregistration
        self.loadZCML(package=netsight.conferenceregistration)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(
            portal, 'netsight.conferenceregistration:default')

        testing.login(aq_parent(portal), 'admin')
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.doActionFor(portal.sponsorships, 'publish')
        testing.logout()

CONFERENCE_FIXTURE = ConferenceFixture()
CONFERENCE_FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(CONFERENCE_FIXTURE,), name="Conference:Functional")
