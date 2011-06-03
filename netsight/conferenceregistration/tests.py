import unittest2 as unittest
import doctest

from netsight.conferenceregistration import testing

optionflags = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)


def test_suite():
    install_suite = doctest.DocFileSuite(
        optionflags=optionflags)
    install_suite.layer = testing.CONFERENCE_FUNCTIONAL_TESTING
    return unittest.TestSuite([install_suite])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
