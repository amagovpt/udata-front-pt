from flask_security.forms import RegisterForm, SendConfirmationForm, ForgotPasswordForm
from flask_wtf import recaptcha
from udata.forms import fields
from udata.forms import validators
from udata.i18n import lazy_gettext as _


class ExtendedRegisterForm(RegisterForm):
    first_name = fields.StringField(
        _('First name'), [validators.DataRequired(_('First name is required')),
                          validators.NoURLs(_('URLs not allowed in this field'))])
    last_name = fields.StringField(
        _('Last name'), [validators.DataRequired(_('Last name is required')),
                         validators.NoURLs(_('URLs not allowed in this field'))])
    recaptcha = recaptcha.RecaptchaField()


class ExtendedSendConfirmationForm(SendConfirmationForm):
    recaptcha = recaptcha.RecaptchaField()
    
class ExtendedForgotPasswordForm(ForgotPasswordForm):
    recaptcha = recaptcha.RecaptchaField()