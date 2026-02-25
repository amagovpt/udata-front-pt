import inspect
from importlib import import_module
from flask import abort, current_app, request
from flask_navigation import Navigation
from authlib.integrations.flask_client import OAuth
from udata import entrypoints
# included for retro-compatibility reasons (some plugins may import from here instead of udata)
from udata.frontend import template_hook  # noqa
from udata.i18n import I18nBlueprint
from udata_front.forms import ExtendedSendConfirmationForm
from .markdown import init_app as init_markdown

nav = Navigation()
oauth = OAuth()

front = I18nBlueprint('front', __name__)


@front.app_context_processor
def inject_current_theme():
    from udata_front import theme
    return {'current_theme': theme.current}


@front.app_context_processor
def inject_cache_duration():
    return {
        'cache_duration': 60 * current_app.config['TEMPLATE_CACHE_DURATION']
    }


def _load_views(app, module):
    views = module if inspect.ismodule(module) else import_module(module)
    blueprint = getattr(views, 'blueprint', None)
    if blueprint:
        app.register_blueprint(blueprint)


VIEWS = ['gouvfr', 'dataset', 'dataservice', 'organization', 'follower', 'post',
         'reuse', 'site', 'territories', 'topic', 'user', 'proconnect']


def init_app(app):
    from udata_front import theme

    nav.init_app(app)
    theme.init_app(app)
    init_markdown(app)

    from . import helpers, error_handlers, menu_helpers, resource_helpers  # noqa

    for view in VIEWS:
        _load_views(app, 'udata_front.views.{}'.format(view))

    # Load all plugins views and blueprints
    for module in entrypoints.get_enabled('udata.views', app).values():
        _load_views(app, module)

    # Optionally register debug views
    if app.config.get('DEBUG'):
        @front.route('/403/')
        def test_403():
            abort(403)

        @front.route('/404/')
        def test_404():
            abort(404)

        @front.route('/500/')
        def test_500():
            abort(500)

    # Load front only views and helpers
    app.register_blueprint(front)

    # Enable CDN if required
    if app.config['CDN_DOMAIN'] is not None:
        from flask_cdn import CDN
        CDN(app)

    # Load debug toolbar if enabled
    if app.config.get('DEBUG_TOOLBAR'):
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)

    # if app.config.get('CAPTCHETAT_BASE_URL'):
        # Security override init
    from udata.auth import security
    from udata_front.forms import ExtendedRegisterForm, ExtendedForgotPasswordForm
    with app.app_context():
        security.forms['register_form'].cls = ExtendedRegisterForm
        security.forms['confirm_register_form'].cls = ExtendedRegisterForm
        security.forms['send_confirmation_form'].cls = ExtendedSendConfirmationForm
        security.forms['forgot_password_form'].cls = ExtendedForgotPasswordForm


    if app.config.get('PROCONNECT_OPENID_CONF_URL'):
        # ProConnect SSO
        oauth.init_app(app)
        oauth.register(
            name='proconnect',
            client_id=app.config.get('PROCONNECT_CLIENT_ID'),
            client_secret=app.config.get('PROCONNECT_CLIENT_SECRET'),
            server_metadata_url=app.config.get('PROCONNECT_OPENID_CONF_URL'),
            client_kwargs={
                'scope': app.config.get('PROCONNECT_SCOPE')
            }
        )

    # === MONKEYPATCH: Segurança SVG e XML ===
    try:
        import os
        import io
        import logging
        from datetime import datetime
        from flask import request
        from udata.core.dataset.models import Checksum, CHECKSUM_TYPES
        from udata.core.storages import api as storage_api
        from udata.core import storages
        from udata.core.dataset.api import UploadMixin
        from udata.api import api
        from udata_front.security import sanitize_svg, sanitize_xml

        log = logging.getLogger(__name__)

        def patched_handle_upload(self, dataset):
            """
            Versão corrigida de handle_upload para sanitizar SVGs e XMLs.
            Substitui o método original para permitir ficheiros seguros.
            """
            if "file" in request.files:
                file_storage = request.files["file"]
                filename = getattr(file_storage, "filename", "").lower()
                mimetype = getattr(file_storage, "mimetype", "")

                if mimetype == "image/svg+xml" or filename.endswith(".svg"):
                    log.info(f"Processando e sanitizando upload de SVG: {filename}")
                    try:
                        content = file_storage.read()
                        cleaned_content = sanitize_svg(content)
                        file_storage.stream = io.BytesIO(cleaned_content)
                        file_storage.seek(0)
                    except ValueError as e:
                        log.error(f"Segurança: SVG rejeitado {filename}: {e}")
                        api.abort(400, f"Ficheiro SVG rejeitado: {str(e)}")

                elif mimetype in ("application/xml", "text/xml") or filename.endswith(".xml"):
                    log.info(f"Processando e sanitizando upload de XML: {filename}")
                    try:
                        content = file_storage.read()
                        cleaned_content = sanitize_xml(content)
                        file_storage.stream = io.BytesIO(cleaned_content)
                        file_storage.seek(0)
                    except ValueError as e:
                        log.error(f"Segurança: XML rejeitado {filename}: {e}")
                        api.abort(400, f"Ficheiro XML rejeitado: {str(e)}")
                    except Exception as e:
                        log.error(f"Erro Crítico ao sanitizar {filename}: {e}")
                        api.abort(400, "Erro ao processar ficheiro XML.")

            prefix = "/".join((dataset.slug, datetime.utcnow().strftime("%Y%m%d-%H%M%S")))
            infos = storage_api.handle_upload(storages.resources, prefix)

            if "html" in infos["mime"]:
                api.abort(415, "Incorrect file content type: HTML")

            infos["title"] = os.path.basename(infos["filename"])
            checksum_type = next(ct for ct in CHECKSUM_TYPES if ct in infos)
            infos["checksum"] = Checksum(type=checksum_type, value=infos.pop(checksum_type))
            infos["filesize"] = infos.pop("size")
            del infos["filename"]

            return infos

        UploadMixin.handle_upload = patched_handle_upload
        log.info("Monkeypatch aplicado: UploadMixin.handle_upload agora sanitiza SVGs.")

    except ImportError as e:
        import logging
        logging.getLogger(__name__).warning(f"Segurança - Monkeypatch ignorado devido a erro de importação: {e}")
