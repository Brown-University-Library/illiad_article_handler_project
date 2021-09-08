import logging, pprint
from django.conf import settings


log = logging.getLogger(__name__)


class Shibber():

    def __init__( self ):
        pass

    def prep_shib_dct( self, request_meta_dct, host ):
        """ Returns dct from shib-info.
            Called by views.handler() """
        log.debug( 'starting manager-def' )
        ( shib_dct, err ) = ( {}, '' )
        ( cleaned_meta_dct, err ) = self.clean_meta_dct( request_meta_dct, host )
        if err:
            log.debug( f'returning err, ``{err}``' )
            return ( shib_dct, err )
        ( shib_dct, err ) = self.validate_shib_dct( cleaned_meta_dct )
        log.debug( 'returning from manager-def' )
        return ( shib_dct, err )

    def clean_meta_dct( self, request_meta_dct, host ):
        """ Returns dct from shib-info.
            Called by prep_shib_dct() """
        log.debug( 'starting clean_meta_dct()' )
        ( cleaned_meta_dct, err ) = ( {}, '' )
        try:
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
            err = 'problem with shibboleth info'
            log.exception( err )
        log.debug( f'cleaned_meta_dct, ``{pprint.pformat(cleaned_meta_dct)}``; err, ``{err}``' )
        return ( cleaned_meta_dct, err )

    def validate_shib_dct( self, shib_dct ):
        """ Checks that minimal info for ILLiad is present.
            Called by prep_shib_dct() """
        ( shib_dct, err ) = ( shib_dct, '' )
        try:
            assert type(shib_dct) == dict
            if 'Shibboleth-eppn' not in shib_dct.keys():
                err = 'missing `eppn` (`authID`)'
            elif 'Shibboleth-mail' not in shib_dct.keys():
                err = 'missing `email`'
        except:
            err = 'problem validating shib info'
            log.exception( err )
        log.debug( f'shib_dct, ``{pprint.pformat(shib_dct)}``; err, ``{err}``' )
        return ( shib_dct, err )

    ## end class Shibber()
