# Python Standard Library Imports
from datetime import datetime
from decimal import Decimal

# Django and Other Third-Party Import
from django.contrib.auth import logout
from django.contrib.auth.views import (
    LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView, PasswordResetDoneView
)

from django.shortcuts import redirect, render
from django.urls import reverse

# App-Specific Imports
from .forms import (
    LoginForm, RegistrationForm, UserPasswordChangeForm, 
    UserPasswordResetForm, UserSetPasswordForm
)

from django_ratelimit.decorators import ratelimit

# CAPTCHA VALIDATION (Seems necessary for your reCAPTCHA implementation)
from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import Assessment

def create_assessment(
    token: str, 
    recaptcha_action: str
    ) -> Assessment:
    """Create an assessment to analyze the risk of a UI action.
    Args:
        project_id: Your Google Cloud Project ID.
        recaptcha_key: The reCAPTCHA key associated with the site/app
        token: The generated token obtained from the client.
        recaptcha_action: Action name corresponding to the token.
    """
    project_id = "mycenter-1703689109632"
    recaptcha_key = "6LdVbj0pAAAAABFEjcwsgfRuurG-k7MU4HplH_1y"

    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    # Set the properties of the event to be tracked.
    event = recaptchaenterprise_v1.Event()
    event.site_key = recaptcha_key
    event.token = token

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_name = f"projects/{project_id}"

    # Build the assessment request.
    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    response = client.create_assessment(request)

    # Check if the token is valid.
    if not response.token_properties.valid:
        print(
            "The CreateAssessment call failed because the token was "
            + "invalid for the following reasons: "
            + str(response.token_properties.invalid_reason)
        )
        return

    # Check if the expected action was executed.
    if response.token_properties.action != recaptcha_action:
        print(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return
    else:
        # Get the risk score and the reason(s).
        # For more information on interpreting the assessment, see:
        # https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment
        for reason in response.risk_analysis.reasons:
            print(reason)
        print(
            "The reCAPTCHA score for this token is: "
            + str(response.risk_analysis.score)
        )
        # Get the assessment name (id). Use this to annotate the assessment.
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")
    return response


# AUTHENTICATION =============================================================
def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


@ratelimit(key='ip', rate='5/h', method='POST', block=False)
def register(request):
    was_limited = getattr(request, 'limited', False)
    context = {'was_limited': was_limited}

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if was_limited:
            context['error_message'] = "You have created many accounts in a short time. Please wait an hour to create more!"
        else:
            recaptcha_token = request.POST.get('g-recaptcha-response')
            #assessment = create_assessment(token=recaptcha_token, recaptcha_action='submit')
            #print(assessment)
            if form.is_valid():            
                form.save()
                print('Account created successfully!')
                context['account_message'] = "You have successfully created a new account to Mycenter! Sign in now!"
            else:
                print("Register failed!")
    else:
        form = RegistrationForm()
    context['form'] = form

    context['is_register'] = True
    context['title'] = "Sign up"
    context['page_title'] = "Create new account to Mycenter"
    context['button_name'] = "Create new account"
    return render(request, 'pages/account.html', context)

def logout_view(request):
  logout(request)
  return redirect('login')

class UserLoginView(LoginView):
    template_name = 'pages/account.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_log_in'] = True
        context['title'] = "Log in"
        context['page_title'] = "Log in to Mycenter"
        context['button_name'] = "Log in"
        return context

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            # Session will expire after 30 days
            self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
        else:
            # Session will expire when the user closes the browser
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def get_success_url(self):
        # Add your logic here to determine the dynamic redirect URL based on user conditions
        if is_admin(self.request.user):
            return reverse('dashboard')  # Example: Redirect staff users to the admin interface
        else:
            return reverse('dashboard')  # Example: Redirect other users to a dashboard


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'pages/account.html'
    form_class = UserPasswordChangeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Change password"
        context['page_title'] = "Change password"
        context['button_name'] = "Change"
        return context

    def form_valid(self, form):
        # Call the superclass form_valid to handle the password change
        response = super().form_valid(form)
        logout(self.request)
        # Redirect to the success URL
        return response

def password_change_done(request):
    context = {'account_message': "You have changed your password successfully. Log in now with your new password!"}
    return render(request, 'pages/account.html', context)


class UserPasswordResetView(PasswordResetView):
    template_name = 'pages/account.html'
    form_class = UserPasswordResetForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reset password"
        context['page_title'] = "Reset password"
        context['button_name'] = "Reset"
        return context

  
class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'pages/account.html'
    form_class = UserPasswordResetForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reset password done"
        context['page_title'] = "Email Sent"
        context['account_message'] = "An email has been sent to your email address. Please click the link and reset your password then log in with the new password you created."
        return context

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'pages/account.html'
    form_class = UserSetPasswordForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reset password"
        context['page_title'] = "Reset password"
        context['button_name'] = "Reset"
        return context


class UserPasswordResetCompleteView(PasswordResetDoneView):
    template_name = 'pages/account.html'
    form_class = UserPasswordResetForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Password Changed"
        context['page_title'] = "Password Changed"
        context['account_message'] = "Your password has been changed successfully. Login again."
        return context












