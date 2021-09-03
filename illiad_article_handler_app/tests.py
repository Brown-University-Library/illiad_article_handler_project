import logging

# from django.test import TestCase
from django.test import SimpleTestCase as TestCase    ## TestCase requires db, this doesn't


log = logging.getLogger(__name__)


class Url_Test( TestCase ):
    """ Checks redirect output. """

    def test_redirect(self):
        """ Checks that redirect is returned. """
        response = self.client.get( '/handler/', {'ItemTitle': 'some title' } )  # project root part of url is assumed
        self.assertEqual( 302, response.status_code )  # permanent redirect
        self.assertEqual( 'https://jcbl.aeon.atlas-sys.com/aeon.dll?ItemTitle=some+title', response.headers['Location'] )

    def test_colon(self):
        """ Checks that colon is encoded. """
        response = self.client.get( '/handler/', {'ItemTitle': 'some: title' } )  # project root part of url is assumed
        self.assertEqual( 'https://jcbl.aeon.atlas-sys.com/aeon.dll?ItemTitle=some%3A+title', response.headers['Location'] )

    def test_long_title(self):
        """ Checks long title.
            <https://brown.primo.exlibrisgroup.com/discovery/fulldisplay?docid=alma991031554999706966&context=L&vid=01BU_INST:BROWN> """
        self.maxDiff = None
        long_title = """The English-American his travail by sea and land: or, A new survey of the West-India's [sic], : containing a journall of three thousand and three hundred miles within the main land of America. Wherin is set forth his voyage from Spain to St. Iohn de Ulhua; and from thence to Xalappa, to Tlaxcalla, the City of Angeles, and forward to Mexico; with the description of that great city, as it was in former times, and also at this present. Likewise his journey from Mexico through the provinces of Guaxaca, Chiapa, Guatemala, Vera Paz, Truxillo, Comayagua; with his abode twelve years about Guatemala, and especially in the Indian-towns of Mixco, Pinola, Petapa, Amatitlan. As also his strange and wonderfull conversion, and calling from those remote parts to his native countrey. With his return through the province of Nicaragua, and Costa Rica, to Nicoya, Panama, Portobelo, Cartagena, and Havana, with divers occurrents and dangers that did befal in the said journey. Also, a new and exact discovery of the Spanish navigation to those parts; and of their dominions, government, religion, forts, castles, ports, havens, commodities, fashions, behaviour of Spaniards, priests, and friers, blackmores, mulatto's, mestiso's, Indians; and of their feasts and solemnities. With a grammar, or some few rudiments of the Indian tongue, called, Poconchi, or Pocoman."""
        response = self.client.get( '/handler/', {'ItemTitle': long_title } )  # project root part of url is assumed
        self.assertEqual( 'https://jcbl.aeon.atlas-sys.com/aeon.dll?ItemTitle=The+English-American+his+travail+by+sea+and+land%3A+or%2C+A+new+survey+of+the+West-India%27s+%5Bsic%5D%2C+%3A+c...', response.headers['Location'] )
