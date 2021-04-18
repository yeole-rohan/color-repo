class LoginFormMiddleware(object):
    def __init__(self, get_response):
            self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        from django.contrib.auth.forms import AuthenticationForm
        if request.method == 'POST' and request.POST.has_key('base-account') and request.POST['base-account'] == 'Login':
            form = AuthenticationForm(data=request.POST, prefix="login")
            if form.is_valid():
                from django.contrib.auth import login
                login(request, form.get_user())
            request.method = 'GET'
        else:
            form = AuthenticationForm(request, prefix="login")
        request.login_form = form
            
    def process_exception(self, request, exception):
        return None
    def process_template_response(self, request, response):
        response.context_data['title'] = 'We changed the title'
        return response