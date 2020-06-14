from django.views.generic import TemplateView


class LoginCancelledView(TemplateView):
    """
    Template view for showing login cancelled error
    """
    template_name = 'login_cancelled.html'


class LoginErrorView(TemplateView):
    """
    Template view for showing general authentication errors. If the raised
    exception contains a message, it will be rendered on the template.
    """
    template_name = 'authentication_error.html'


login_error = LoginErrorView.as_view()
login_cancelled = LoginCancelledView.as_view()
