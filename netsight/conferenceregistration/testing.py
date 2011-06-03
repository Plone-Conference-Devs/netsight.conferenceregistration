from plone.app import testing


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

CONFERENCE_FIXTURE = ConferenceFixture()
CONFERENCE_FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(CONFERENCE_FIXTURE,), name="Conference:Functional")
