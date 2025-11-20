from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_URLS = [
    reverse('login'),      # login page
    reverse('logout'),     # logout page
    '/admin/',             # allow admin
    '/static/',            # allow static files
]

class LoginRequiredMiddleware:
    def _init_(self, get_response):
        self.get_response = get_response

    def _call_(self, request):
        path = request.path
        if not request.user.is_authenticated:
            if not any(path.startswith(url) for url in EXEMPT_URLS):
                return redirect('login')
        response = self.get_response(request)
        return response