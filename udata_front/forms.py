from flask_security.forms import RegisterForm, SendConfirmationForm, ForgotPasswordForm, LoginForm
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

    def validate(self, **kwargs):
        if not super(ExtendedSendConfirmationForm, self).validate(**kwargs):
            # Se for um erro de email (ex: utilizador não existe), removemos o erro
            # para evitar enumeração de utilizadores.
            if 'email' in self.errors:
                self.errors.pop('email')
                return True
            return False
        return True
    
class ExtendedForgotPasswordForm(ForgotPasswordForm):
    recaptcha = recaptcha.RecaptchaField()

    def validate(self, **kwargs):
        if not super(ExtendedForgotPasswordForm, self).validate(**kwargs):
            # Se for um erro de email (ex: utilizador não existe), removemos o erro
            # para evitar enumeração de utilizadores.
            if 'email' in self.errors:
                self.errors.pop('email')
                return True
            return False
        return True
class ExtendedLoginForm(LoginForm):
    def validate(self, **kwargs):
        if not super(ExtendedLoginForm, self).validate(**kwargs):
            # Unificar mensagens de erro para evitar enumeração.
            # Se houver erro no email ou senha, mostramos uma mensagem genérica.
            if 'email' in self.errors or 'password' in self.errors:
                self.errors.pop('email', None)
                self.errors.pop('password', None)
                # Adicionamos o erro genérico aos erros globais do formulário
                self.form_errors.append(_('Invalid email or password.'))
                return False
            return False
        return True
