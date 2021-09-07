def grab_pattern_header( feedback_url ) -> str:
    """ Prepares html for header.
        Called by a few helper.prepare_context() functions. """
    assert type( feedback_url ) == str
    cache_key = 'pattern_header'
    header_html = cache.get( cache_key, None )
    if header_html:
        log.debug( 'pattern-header in cache' )
    else:
        log.debug( 'pattern-header not in cache' )
        r = requests.get( settings.PATTERNLIB_HEADER_URL )
        header_html = r.content.decode( 'utf8' )
        header_html = header_html.replace( 'DYNAMIC__FEEDBACK', feedback_url )
        cache.set( cache_key, header_html, settings.PATTERNLIB_HEADER_CACHE_TIMEOUT )
    return header_html
