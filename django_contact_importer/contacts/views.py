# Create your views here.

from django.shortcuts import redirect, render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from contact_importer.providers import (GoogleContactImporter, 
                                        YahooContactImporter, 
                                        LiveContactImporter)

providers = {
    "google": GoogleContactImporter,
    "live": LiveContactImporter,
    "yahoo": YahooContactImporter
}

def index(request):
    provider = request.GET.get('provider')
    if provider:
        provider_instance = _get_provider_instance(provider, _get_redirect_url(request))
        if provider == "yahoo":
            provider_instance.get_request_token()
            request.session["oauth_token_secret"] = provider_instance.oauth_token_secret
        return redirect(provider_instance.request_authorization())
    return render_to_response("contacts/index.html")

def invite(request):
    provider = request.GET.get('provider')

    if not provider:
        return redirect(reverse("contacts_index"))

    code = request.GET.get('code')
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')
    redirect_url = _get_redirect_url(request)
    provider_instance = _get_provider_instance(provider, redirect_url)

    if provider == "yahoo":
        provider_instance.oauth_token = oauth_token
        provider_instance.oauth_verifier = oauth_verifier
        provider_instance.oauth_token_secret = request.session["oauth_token_secret"]
        provider_instance.get_token()
        contacts = provider_instance.import_contacts()
        del request.session["oauth_token_secret"]
    else:
        access_token = provider_instance.request_access_token(code)
        contacts = provider_instance.import_contacts(access_token)

    return render_to_response("contacts/invite.html", {"contacts": contacts})

def _get_redirect_url(request):
        provider = request.GET.get('provider')
        invite_url = "%s?provider=%s" % (reverse("invite_contacts"), provider)
        request_scheme = "https" if request.is_secure() else "http"
        redirect_url = "%s://%s%s" % (request_scheme, request.META["HTTP_HOST"], invite_url)
        return redirect_url

def _get_provider_instance(provider, redirect_url):    
    if provider not in providers:
        raise Exception("The provider %s is not supported." % provider)

    client_id = getattr(settings, "%s_CLIENT_ID" % provider.upper(), None)
    client_secret = getattr(settings, "%s_CLIENT_SECRET" % provider.upper(), None)

    if not client_id:
        raise Exception("The provider %s is not supported." % provider)

    provider_class = providers[provider]
    return provider_class(client_id, client_secret, redirect_url)