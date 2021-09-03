import logging, pprint

import django  # for type() test
from django.conf import settings as project_settings
from django.http import HttpResponse, HttpResponseRedirect


log = logging.getLogger(__name__)


def handler(request):
    """ Truncates long title if necessary, and redirects to JCB Aeon.
        Possible future TODO...
        - Add sid (source-id) param in Alma to indicating that the link a JCB or Aeon link.
        - inspect that, and redirect to proper Aeon instance.
    """
    log.debug( f'request.GET, ``{pprint.pformat(request.GET)}``' )
    ## Make copy of QueryDict (which is immutable) --------
    params_query_dict_copy = request.GET.copy()  # <https://stackoverflow.com/questions/5036498/django-rebuild-a-query-string-without-one-of-the-variables>
    assert type(params_query_dict_copy) == django.http.request.QueryDict, type(params_query_dict_copy)
    log.debug( f'params_query_dict_copy initially, ``{pprint.pformat(params_query_dict_copy)}``' )
    ## Truncate title if necessary ------------------------
    truncated_title = ''
    if 'ItemTitle' in params_query_dict_copy.keys():
        title = params_query_dict_copy['ItemTitle']
        if len( title ) > project_settings.TRUNCATE_LENGTH:
            len_minus_elipsis = project_settings.TRUNCATE_LENGTH - 3
            truncated_title = f'{title[0:len_minus_elipsis]}...'
            params_query_dict_copy['ItemTitle'] = truncated_title
    log.debug( f'params_query_dict_copy now, ``{pprint.pformat(params_query_dict_copy)}``' )
    ## Recreate encoded parameter string ------------------
    encoded_qd = params_query_dict_copy.urlencode()
    assert type(encoded_qd) == str, type(encoded_qd)
    log.debug( f'encoded_qd, ``{encoded_qd}``' )
    ## Redirect to JCB Aeon -------------------------------
    redirect_url = f'https://jcbl.aeon.atlas-sys.com/aeon.dll?{encoded_qd}'
    return HttpResponseRedirect( redirect_url )


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


def version(request):
    return HttpResponse( 'version response coming' )


def info(request):
    return HttpResponse( 'info response coming' )
