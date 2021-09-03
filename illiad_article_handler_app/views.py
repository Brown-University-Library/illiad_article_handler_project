import logging, pprint

import django  # for type() test
from django.conf import settings as project_settings
from django.http import HttpResponse, HttpResponseRedirect


log = logging.getLogger(__name__)


def handler(request):
    """ Creates ILLiad new-user if necessary, then redirects user to ILLiad form.
    """
    log.debug( f'request.GET, ``{pprint.pformat(request.GET)}``' )
    ## Make copy of QueryDict (which is immutable) --------
    params_query_dict_copy = request.GET.copy()  # <https://stackoverflow.com/questions/5036498/django-rebuild-a-query-string-without-one-of-the-variables>
    assert type(params_query_dict_copy) == django.http.request.QueryDict, type(params_query_dict_copy)
    log.debug( f'params_query_dict_copy initially, ``{pprint.pformat(params_query_dict_copy)}``' )
    ## check for new ILLiad user
    ## create new ILLiad user if necessary
    ## redirect to ILLiad form
    return HttpResponse( 'handler coming' )


def info(request):
    return HttpResponse( 'info response coming' )


## for developemnt convenience ------------------------------------------------


def error_check( request ):
    """ For an easy way to check that admins receive error-emails.
        To view error-emails in runserver-development:
        - run, in another terminal window: `python3 -m smtpd -n -c DebuggingServer localhost:1026`,
          (or substitute your own settings for localhost:1026)
    """
    log.debug( f'project_settings.DEBUG, ``{project_settings.DEBUG}``' )
    if project_settings.DEBUG == True:
        raise Exception( 'error-check triggered; admin emailed' )
    else:
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )


def version(request):
    return HttpResponse( 'version response coming' )
