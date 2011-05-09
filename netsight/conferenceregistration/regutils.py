from zope.app.component.hooks import getSite


def getConferenceYear():
    """ Return the conference year for this site """
    portal = getSite()
    if not portal:
        # then grok is doing something weird
        return ''
    return portal.portal_properties.conference_properties.getProperty('year')