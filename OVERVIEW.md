# ILLiad Article Handler Overview

## Purpose

This Django webapp acts as a small request router in front of ILLiad.

Its main job is to:

- accept an incoming OpenURL-style request
- derive user identity data from Shibboleth request metadata
- check the user’s ILLiad status through an internal ILLiad API
- create a new ILLiad user when needed
- redirect the browser to the public ILLiad request form with the original query parameters preserved
- show a user-facing error page when prerequisite checks fail

In practice, this app does very little page rendering. The normal success path is a redirect to ILLiad.

## Top-Level Entry Points

The URL configuration in `config/urls.py` exposes five routes:

- `openurl/`
  - mapped to `views.handler`
  - this is the primary application entry point
  - expected to receive incoming request parameters that should ultimately be forwarded to ILLiad

- `message/`
  - mapped to `views.message`
  - renders a user-facing problem page
  - usually reached via redirect from `views.handler`

- `error_check/`
  - mapped to `views.error_check`
  - development/admin helper to deliberately trigger an exception when `DEBUG` is `True`

- `info/`
  - mapped to `views.info`
  - simple placeholder response

- `version/`
  - mapped to `views.version`
  - simple placeholder response

## Main Request Flow: `openurl/` -> `views.handler`

`views.handler(request)` is the authoritative request-processing function.

### Inputs

It relies on two parts of the Django request:

- `request.GET`
  - copied and preserved for later redirect construction
- `request.META`
  - used as the source of Shibboleth attributes

### Step 1: Preserve incoming query parameters

The view copies `request.GET` into a Django `QueryDict` named `params_query_dict_copy`.

That copy is later URL-encoded and appended to the public ILLiad URL, so the original request metadata is forwarded downstream.

### Step 2: Build user data from Shibboleth headers

The view instantiates `Shibber` from `illiad_article_handler_app.lib.shib_handler` and calls:

- `Shibber.prep_shib_dct(request.META, request.get_host())`

That method performs three sub-steps:

#### 2a. `clean_meta_dct()`

- validates that metadata is a dict and `host` is a string
- if running on `127.0.0.1`, `127.0.0.1:8000`, or `testserver`, it substitutes `settings.DEV_SHIB_DCT`
- otherwise it copies `request.META` and removes keys containing `passenger` or `wsgi.` so the dict is cleaner and more serializable

If this step fails, it returns:

- empty user dict
- error string: `problem with shibboleth info`

#### 2b. `validate_shib_dct()`

This checks for the minimum Shibboleth attributes required by the app:

- `Shibboleth-eppn`
- `Shibboleth-mail`

Failure returns one of these error strings:

- `missing \`eppn\` (\`authID\`)`
- `missing \`email\``
- `problem validating shib info`

#### 2c. `make_user_dct()`

This normalizes the Shibboleth fields into a simpler `user_dct` with keys:

- `eppn`
- `email`
- `first_name`
- `last_name`
- `brown_type`
- `phone`
- `department`

If any error occurred in steps 2a or 2b, `views.handler` immediately redirects to `message/` through `HandlerHelper.create_problem_response()`.

### Step 3: Check ILLiad user status and possibly create a user

The view instantiates `IlliadUserManager` from `illiad_article_handler_app.lib.illiad_helper` and calls:

- `IlliadUserManager.manage_illiad_user_check(user_dct)`

This method is the main ILLiad integration manager.

#### 3a. `check_illiad_status()`

This method calls the internal ILLiad API at:

- `settings.ILLIAD_API_URL_ROOT + 'check_user/'`

Request characteristics:

- HTTP method: `GET`
- query params: `{ 'user': auth_id }`
- Basic Auth credentials from Django settings
- custom `User-Agent` from settings
- timeout: 10 seconds

The username sent to the API is derived from:

- `usr_dct['eppn'].split('@')[0]`

Expected response shape includes at least:

- `response.status_data.blocked`
- `response.status_data.disavowed`
- `response.status_data.interpreted_new_user`

If the HTTP call itself fails, the helper logs the exception and returns a fallback dict with only:

- `blocked: None`
- `disavowed: None`

That fallback shape is incomplete for later access to `interpreted_new_user`, so the manager may then fall into its exception handler and return the generic error `problem with ILLiad new-user check`.

#### 3b. Decision logic inside `manage_illiad_user_check()`

After status retrieval:

- if `blocked` is `True` or `disavowed` is `True`
  - returns the error string `problem with ILLiad status`
- else if `interpreted_new_user` is `True`
  - calls `manage_new_user(usr_dct)`
- else
  - treats the user as ready and records success internally

The method ultimately returns an error string, not a rich result object:

- `''` for success or non-fatal continuation
- `problem with ILLiad status` for blocked/disavowed users
- `problem with ILLiad new-user check` for exceptions during status/new-user logic

#### 3c. `manage_new_user()` and `create_new_user()`

If the ILLiad status API says the user is new, the app attempts to create the user via:

- `create_new_user(usr_dct)`

That method:

- builds a POST payload via `setup_create_user()`
- calls `settings.ILLIAD_API_URL_ROOT + 'create_user/'`
- treats the operation as successful only if the response JSON contains status `registered`

Request characteristics:

- HTTP method: `POST`
- timeout: 10 seconds

The payload assembled in `setup_create_user()` is intended to include:

- `auth_key`
- `auth_id`
- `first_name`
- `last_name`
- `email`
- `status`
- `phone`
- `department`

### Important implementation caveat in new-user creation

There is a key mismatch between the Shibboleth normalization layer and the ILLiad create-user payload builder:

- `Shibber.make_user_dct()` produces:
  - `first_name`
  - `last_name`
- `IlliadUserManager.setup_create_user()` expects:
  - `name_first`
  - `name_last`

Because of that mismatch, a newly detected user will likely raise a `KeyError` during payload setup, which is then caught by `manage_illiad_user_check()` and returned as:

- `problem with ILLiad new-user check`

However, `views.handler()` explicitly treats only one error as fatal:

- `problem with ILLiad status`

Its inline note says that when the error is `problem with ILLiad new-user check`, processing continues. So in the current implementation, a failure during new-user creation does not necessarily stop the redirect to ILLiad.

### Step 4: Build redirect to public ILLiad form

If no fatal status problem is detected, `views.handler()` calls:

- `HandlerHelper.create_illiad_redirect_url(params_query_dict_copy)`

This helper:

- asserts the input is a Django `QueryDict`
- URL-encodes it with `.urlencode()`
- concatenates it onto `settings.ILLIAD_PUBLIC_URL_ROOT`

Returned tuple:

- `(redirect_url, '')` on success
- `('', 'problem preparing ILLiad redirect')` on failure

If successful, the view returns:

- `HttpResponseRedirect(redirect_url)`

So the normal successful response from `openurl/` is an HTTP redirect to the public ILLiad endpoint with the original request query string attached.

### Error handling from `handler()`

When `handler()` decides it cannot continue, it calls:

- `HandlerHelper.create_problem_response(err)`

That helper does not render a page directly. Instead it:

- URL-encodes the error text
- builds `reverse('message_url') + '?problem=...'`
- returns `HttpResponseRedirect` to `message/`

So the main view’s failure mode is also a redirect, not a direct error page response.

## Problem Page Flow: `message/` -> `views.message`

`views.message(request)` is a simple renderer for user-facing error output.

### Inputs

It expects a required query parameter:

- `problem`

It reads it directly with:

- `request.GET['problem']`

That means a direct visit to `message/` without the parameter would raise a `KeyError`.

### Context-building logic

The view calls:

- `message_helper.grab_pattern_header()`

This helper:

- checks Django cache for the key `pattern_header`
- if absent, fetches HTML from `settings.PATTERNLIB_HEADER_URL` using `requests.get()`
- decodes the HTML as UTF-8
- caches it for `settings.PATTERNLIB_HEADER_CACHE_TIMEOUT`

The view then renders `message.html` with:

- `problem`
- `pattern_header`

### Output

The response is:

- `render(request, 'message.html', context)`

The template displays a friendly failure message saying there was a problem preparing the article request, includes the lowercased problem text, and provides Brown Library interlibrary loan contact details.

## Helper/Diagnostic Endpoints

### `info/` -> `views.info`

Returns:

- plain `HttpResponse('info response coming')`

This is a placeholder endpoint with no additional logic.

### `version/` -> `views.version`

Returns:

- plain `HttpResponse('version response coming')`

This is also a placeholder endpoint with no additional logic.

### `error_check/` -> `views.error_check`

Purpose:

- development/admin helper to test that exception emails are sent to admins

Behavior:

- if `project_settings.DEBUG == True`
  - raises `Exception('error-check triggered; admin emailed')`
- else
  - attempts to return `HttpResponseNotFound('<div>404 / Not Found</div>')`

Note that `HttpResponseNotFound` is not imported in `views.py`, so the non-debug branch would fail with `NameError` if reached.

## External Dependencies and Configuration

The application is heavily configuration-driven through Django settings backed by environment variables.

Important settings used in the traced flow:

- `DEV_SHIB_DCT`
  - fake/local Shibboleth data for development hosts

- `PATTERNLIB_HEADER_URL`
  - remote HTML source for the shared page header

- `PATTERNLIB_HEADER_CACHE_TIMEOUT`
  - cache duration for the fetched header HTML

- `ILLIAD_API_URL_ROOT`
  - base URL for the internal ILLiad API used for status checks and user creation

- `ILLIAD_API_USER_AGENT`
  - outgoing user-agent header for the status-check request

- `ILLIAD_API_BASIC_AUTH_USER`
- `ILLIAD_API_BASIC_AUTH_PASSWORD`
  - Basic Auth credentials for the status-check request

- `ILLIAD_PUBLIC_URL_ROOT`
  - public ILLiad form URL used for the final browser redirect

The code also references `settings.ILLIAD_API_KEY` when creating or updating users, but that setting was not defined in the `config/settings.py` snippet reviewed here. If it is not defined elsewhere at runtime, new-user creation and status-update helpers would fail when they try to access it.

## High-Level Architecture Summary

The app is best understood as a thin Django adapter around two concerns:

- authentication/context extraction from Shibboleth headers
- orchestration of ILLiad API checks before redirecting into ILLiad itself

The internal structure is:

- `views.py`
  - HTTP entry points and response decisions
- `lib/shib_handler.py`
  - Shibboleth metadata cleaning, validation, and normalization
- `lib/illiad_helper.py`
  - ILLiad API status checks and user-creation logic
- `lib/view_handler_helper.py`
  - redirect URL construction for success and failure cases
- `lib/message_helper.py`
  - shared header HTML retrieval and caching for rendered pages

## What the Webapp Returns

From an HTTP perspective, the app mainly returns three kinds of responses:

- redirect to public ILLiad
  - normal `openurl/` success path

- redirect to `message/` with `?problem=...`
  - `openurl/` failure path for Shibboleth validation issues, blocked/disavowed users, or redirect-preparation failures

- rendered HTML page
  - `message/` endpoint via `message.html`

The remaining endpoints return small plain-text responses or intentionally raise an exception for diagnostics.

## Most Important Observations

- `openurl/` is the real production entry point.
- The app is primarily a redirector/orchestrator, not a full UI application.
- Successful processing depends on both Shibboleth metadata and an internal ILLiad API.
- New-user creation appears fragile because of a field-name mismatch between `make_user_dct()` and `setup_create_user()`.
- New-user creation failures are currently non-fatal in `views.handler()`, while blocked/disavowed status is treated as fatal.
- `message/` assumes `problem` is always present in the query string.
- `error_check()` has a likely import bug in its non-debug branch.
