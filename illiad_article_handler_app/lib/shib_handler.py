import logging
from django.conf import settings


log = logging.getLogger(__name__)


class Shibber():

    def __init__( self ):
        pass

    def prep_shib_dct( self, request_meta_dct, host ):
        """ Returns dct from shib-info.
            Called by ConfReqHlpr.save_patron_info() """
        log.debug( 'starting prep_shib_dct()' )
        ( cleaned_meta_dct, err ) = ( {}, '' )
        try:
            1/0
            assert type(request_meta_dct) == dict
            assert type(host) == str
            if host == '127.0.0.1' or host == '127.0.0.1:8000' or host == 'testserver':
                cleaned_meta_dct = settings.DEV_SHIB_DCT
            else:
                # cleaned_meta_dct = copy.copy( request_meta_dct )
                cleaned_meta_dct = request_meta_dct.copy()
                for (key, val) in request_meta_dct.items():  # get rid of some dictionary items not serializable
                    if 'passenger' in key:
                        cleaned_meta_dct.pop( key )
                    elif 'wsgi.' in key:
                        cleaned_meta_dct.pop( key )
        except:
            err = 'Problem with shibboleth info.'
            log.exception( err )
        log.debug( f'cleaned_meta_dct, ``{cleaned_meta_dct}``' )
        log.debug( f'err, ``{err}``' )
        return ( cleaned_meta_dct, err )

