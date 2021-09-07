import logging
from urllib.parse import quote_plus

from django.http import HttpResponseRedirect
from django.urls import reverse


log = logging.getLogger(__name__)


class HandlerHelper():

    def __init__( self ):
        pass

    def create_problem_response( self, err ):
        """ Stores error-message to session, and returns redirect response.
            Called by views.handler() """
        assert type(err) == str
        redirect_url = '%s?problem=%s' % ( reverse('message_url'), quote_plus(err) )
        log.debug( f'redirecting to message url, ``{redirect_url}``' )
        rsp = HttpResponseRedirect( redirect_url )
        return rsp
