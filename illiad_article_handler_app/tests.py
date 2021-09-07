import logging

# from django.test import TestCase (test commit)
from django.test import SimpleTestCase as TestCase    ## TestCase requires db, this doesn't


log = logging.getLogger(__name__)


# class Url_Test( TestCase ):
#     """ Checks redirect output. """

#     def test_redirect(self):
#         """ Checks that redirect is returned. """
#         response = self.client.get( '/handler/', {'ItemTitle': 'some title' } )  # project root part of url is assumed
#         self.assertEqual( 302, response.status_code )  # redirect
#         self.assertEqual( 'https://jcbl.aeon.atlas-sys.com/aeon.dll?ItemTitle=some+title', response.headers['Location'] )

#     def test_colon(self):
#         """ Checks that colon is encoded. """
#         response = self.client.get( '/handler/', {'ItemTitle': 'some: title' } )  # project root part of url is assumed
#         self.assertEqual( 'https://jcbl.aeon.atlas-sys.com/aeon.dll?ItemTitle=some%3A+title', response.headers['Location'] )
