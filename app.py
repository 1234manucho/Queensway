"""Queensway Early Years — Flask application factory and routes."""
import os
import secrets
from datetime import date, timedelta
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

from models import db, AdminUser, Submission, NewsPost
from forms import EnquiryForm, LoginForm, StatusForm, DeleteForm, PostForm
from content import VISION, MISSION, VALUES, PROGRAMMES, GALLERY, ARTICLES, PHOTOS

load_dotenv()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please sign in to access the school office.'
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
DUMMY_HASH = generate_password_hash('unused-' + secrets.token_hex(20))


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    production = os.getenv('APP_ENV') == 'production'
    secret = os.getenv('SECRET_KEY')
    if production and (not secret or len(secret) < 32):
        raise RuntimeError('Set a unique SECRET_KEY of at least 32 characters before production startup.')
    if not secret:
        secret_file = Path(app.instance_path) / '.dev-secret'
        if not secret_file.exists():
            try:
                with secret_file.open('x') as handle:
                    handle.write(secrets.token_hex(32))
                secret_file.chmod(0o600)
            except FileExistsError:
                pass
        secret = secret_file.read_text().strip()
    database = os.getenv('DATABASE_URL', 'sqlite:///queensway.db')
    if database.startswith('postgres://'):
        database = database.replace('postgres://', 'postgresql+psycopg://', 1)
    elif database.startswith('postgresql://'):
        database = database.replace('postgresql://', 'postgresql+psycopg://', 1)
    app.config.update(
        SECRET_KEY=secret, SQLALCHEMY_DATABASE_URI=database,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=production, REMEMBER_COOKIE_SECURE=production,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=4),
        MAX_CONTENT_LENGTH=64 * 1024, WTF_CSRF_TIME_LIMIT=7200,
        RATELIMIT_STORAGE_URI=os.getenv('REDIS_URL', 'memory://'),
        PREVIEW_MODE=False,
        SCHOOL_NAME='Queensway Early Years', SCHOOL_TAGLINE='Inspiring inquisitive minds',
        SCHOOL_EMAIL=os.getenv('SCHOOL_EMAIL', ''), SCHOOL_PHONE=os.getenv('SCHOOL_PHONE', ''),
        SCHOOL_ADDRESS=os.getenv('SCHOOL_ADDRESS', ''), SCHOOL_HOURS=os.getenv('SCHOOL_HOURS', ''),
    )
    if test_config:
        app.config.update(test_config)
    # Trust forwarding headers only when the deployment's proxy count is known.
    proxy_hops = int(os.getenv('TRUSTED_PROXY_HOPS', '0'))
    if proxy_hops > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxy_hops, x_proto=proxy_hops)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    app.jinja_env.globals['school_photos'] = PHOTOS

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(AdminUser, int(user_id))
        except (ValueError, TypeError):
            return None

    @app.context_processor
    def school_context():
        return {'school': app.config, 'vision': VISION, 'mission': MISSION, 'values': VALUES,
                'programmes': PROGRAMMES, 'current_year': date.today().year,
                'preview_mode': app.config['PREVIEW_MODE'], 'delete_form': DeleteForm(),
                'today': date.today().isoformat()}

    @app.after_request
    def secure_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'"
        if production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        if request.path.startswith('/admin') or request.path == '/thank-you/':
            response.headers['Cache-Control'] = 'no-store'
        return response

    def published_posts(limit=None):
        query = db.select(NewsPost).where(NewsPost.published.is_(True)).order_by(NewsPost.created_at.desc())
        if limit:
            query = query.limit(limit)
        return db.session.execute(query).scalars().all()

    @app.get('/')
    def index():
        return render_template('index.html', posts=published_posts(3))

    @app.get('/about/')
    def about():
        return render_template('about.html')

    @app.get('/learning/')
    def learning():
        return render_template('learning.html')

    @app.get('/learning/<slug>/')
    def programme(slug):
        selected = next((p for p in PROGRAMMES if p['slug'] == slug), None)
        if not selected:
            abort(404)
        return render_template('programme.html', programme=selected)

    @app.get('/school-life/')
    def school_life():
        return render_template('school_life.html')

    @app.get('/gallery/')
    def gallery():
        return render_template('gallery.html', gallery=GALLERY)

    @app.get('/journal/')
    def journal():
        return render_template('journal.html', posts=published_posts())

    @app.get('/journal/<slug>/')
    def article(slug):
        post = db.session.execute(db.select(NewsPost).where(NewsPost.slug == slug, NewsPost.published.is_(True))).scalar_one_or_none()
        if not post:
            abort(404)
        return render_template('article.html', post=post)

    def enquiry_page(kind, template):
        form = EnquiryForm()
        if form.validate_on_submit():
            if form.website.data:
                abort(400)
            record = Submission(kind=kind, parent_name=form.parent_name.data.strip(),
                email=form.email.data.strip().lower(), phone=form.phone.data.strip(),
                child_first_name=form.child_first_name.data.strip() if form.child_first_name.data else None,
                age_range=form.age_range.data or None, programme=form.programme.data or None,
                preferred_date=form.preferred_date.data if kind == 'visit' else None,
                message=(form.message.data or '').strip(), consent=form.consent.data)
            db.session.add(record)
            db.session.commit()
            session['confirmation'] = {'reference': record.reference, 'kind': kind}
            return redirect(url_for('thank_you'), code=303)
        return render_template(template, form=form, form_kind=kind), (422 if request.method == 'POST' else 200)

    @app.route('/admissions/', methods=['GET', 'POST'])
    @limiter.limit('8 per hour', methods=['POST'])
    def admissions():
        return enquiry_page('admission', 'admissions.html')

    @app.route('/visit/', methods=['GET', 'POST'])
    @limiter.limit('8 per hour', methods=['POST'])
    def visit():
        return enquiry_page('visit', 'visit.html')

    @app.route('/contact/', methods=['GET', 'POST'])
    @limiter.limit('8 per hour', methods=['POST'])
    def contact():
        return enquiry_page('contact', 'contact.html')

    @app.get('/thank-you/')
    def thank_you():
        confirmation = session.get('confirmation')
        if not confirmation and not app.config['PREVIEW_MODE']:
            return redirect(url_for('contact'))
        return render_template('thank_you.html', confirmation=confirmation)

    @app.get('/privacy/')
    def privacy():
        return render_template('privacy.html')

    @app.get('/health')
    def health():
        db.session.execute(db.text('SELECT 1'))
        return {'status': 'ok'}

    @app.route('/admin/login/', methods=['GET', 'POST'])
    @limiter.limit('5 per minute; 25 per hour', methods=['POST'])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard'))
        form = LoginForm()
        if form.validate_on_submit():
            user = db.session.execute(db.select(AdminUser).where(AdminUser.email == form.email.data.strip().lower())).scalar_one_or_none()
            valid = check_password_hash(user.password_hash if user else DUMMY_HASH, form.password.data)
            if user and valid:
                session.clear()
                login_user(user, remember=False)
                session.permanent = True
                return redirect(url_for('admin_dashboard'))
            flash('The email or password is incorrect.', 'error')
        return render_template('admin/login.html', form=form)

    @app.post('/admin/logout/')
    @login_required
    def admin_logout():
        logout_user()
        session.clear()
        return redirect(url_for('index'))

    @app.get('/admin/')
    @login_required
    def admin_dashboard():
        kind = request.args.get('kind', '')
        status = request.args.get('status', '')
        query = request.args.get('q', '').strip()[:120]
        statement = db.select(Submission)
        if kind in ('contact', 'visit', 'admission'):
            statement = statement.where(Submission.kind == kind)
        if status in ('new', 'contacted', 'closed'):
            statement = statement.where(Submission.status == status)
        if query:
            statement = statement.where(db.or_(Submission.parent_name.icontains(query, autoescape=True), Submission.email.icontains(query, autoescape=True), Submission.reference.icontains(query, autoescape=True)))
        pagination = db.paginate(statement.order_by(Submission.created_at.desc()), per_page=15, error_out=False)
        counts = {k: db.session.scalar(db.select(db.func.count()).select_from(Submission).where(Submission.kind == k)) for k in ('admission', 'visit', 'contact')}
        counts['new'] = db.session.scalar(db.select(db.func.count()).select_from(Submission).where(Submission.status == 'new'))
        return render_template('admin/dashboard.html', pagination=pagination, counts=counts, kind=kind, status=status, query=query)

    @app.route('/admin/enquiries/<int:record_id>/', methods=['GET', 'POST'])
    @login_required
    def admin_submission(record_id):
        record = db.get_or_404(Submission, record_id)
        form = StatusForm(obj=record)
        if form.validate_on_submit():
            record.status = form.status.data
            record.notes = form.notes.data or ''
            db.session.commit()
            flash('Enquiry updated.', 'success')
            return redirect(url_for('admin_submission', record_id=record.id))
        return render_template('admin/submission.html', record=record, form=form)

    @app.post('/admin/enquiries/<int:record_id>/delete/')
    @login_required
    def admin_delete_submission(record_id):
        form = DeleteForm()
        if not form.validate_on_submit():
            abort(400)
        record = db.get_or_404(Submission, record_id)
        db.session.delete(record)
        db.session.commit()
        flash('Enquiry permanently deleted.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.get('/admin/articles/')
    @login_required
    def admin_posts():
        posts = db.session.execute(db.select(NewsPost).order_by(NewsPost.created_at.desc())).scalars().all()
        return render_template('admin/posts.html', posts=posts)

    @app.route('/admin/articles/new/', methods=['GET', 'POST'])
    @app.route('/admin/articles/<int:post_id>/edit/', methods=['GET', 'POST'])
    @login_required
    def admin_post_edit(post_id=None):
        post = db.get_or_404(NewsPost, post_id) if post_id else None
        form = PostForm(obj=post)
        if form.validate_on_submit():
            post = post or NewsPost()
            form.populate_obj(post)
            db.session.add(post)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.slug.errors.append('This URL is already used by another article.')
                if post_id is None:
                    post = None
            else:
                flash('Article saved.', 'success')
                return redirect(url_for('admin_posts'))
        return render_template('admin/post_edit.html', form=form, post=post)

    @app.post('/admin/articles/<int:post_id>/delete/')
    @login_required
    def admin_delete_post(post_id):
        if not DeleteForm().validate_on_submit():
            abort(400)
        db.session.delete(db.get_or_404(NewsPost, post_id))
        db.session.commit()
        flash('Article deleted.', 'success')
        return redirect(url_for('admin_posts'))

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template('error.html', code=400, heading='Let’s try that again', message='Your form session has expired or could not be verified. Reload the form and try again.'), 400

    @app.errorhandler(404)
    @app.errorhandler(413)
    @app.errorhandler(429)
    @app.errorhandler(500)
    def handle_error(error):
        code = getattr(error, 'code', 500)
        messages = {404: ('A little detour', 'We couldn’t find that page. Let’s get you back to something wonderful.'), 413: ('That message is a little too long', 'Please shorten your message and try again.'), 429: ('Please take a little pause', 'Too many requests have been made. Please try again later.'), 500: ('Something needs our attention', 'We couldn’t complete that request. Please try again shortly.')}
        if code == 500:
            db.session.rollback()
        heading, message = messages[code]
        return render_template('error.html', code=code, heading=heading, message=message), code

    @app.cli.command('init-db')
    def init_db():
        """Create missing tables (does not delete existing data)."""
        db.create_all()
        click.echo('Database tables are ready.')

    @app.cli.command('seed-content')
    def seed_content():
        """Add optional evergreen starter articles, without overwriting edits."""
        for data in ARTICLES:
            if not db.session.scalar(db.select(NewsPost).where(NewsPost.slug == data['slug'])):
                db.session.add(NewsPost(**data, published=True))
        db.session.commit()
        click.echo('Starter articles are ready.')

    @app.cli.command('create-admin')
    @click.option('--email', prompt=True)
    @click.password_option(confirmation_prompt=True)
    def create_admin(email, password):
        """Create an administrator; password is entered privately."""
        from email_validator import validate_email, EmailNotValidError
        try:
            email = validate_email(email, check_deliverability=False).normalized.lower()
        except EmailNotValidError as error:
            raise click.ClickException(str(error))
        if len(password) < 12 or len(password) > 256:
            raise click.ClickException('Use a password between 12 and 256 characters.')
        if db.session.scalar(db.select(AdminUser).where(AdminUser.email == email)):
            raise click.ClickException('This administrator already exists. Use reset-admin-password.')
        user = AdminUser(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo('Administrator created.')

    @app.cli.command('reset-admin-password')
    @click.option('--email', prompt=True)
    @click.password_option(confirmation_prompt=True)
    def reset_admin_password(email, password):
        user = db.session.scalar(db.select(AdminUser).where(AdminUser.email == email.strip().lower()))
        if not user or not 12 <= len(password) <= 256:
            raise click.ClickException('Check the account email and use a 12–256 character password.')
        user.set_password(password)
        db.session.commit()
        click.echo('Password updated.')

    return app


if __name__ == '__main__':
    create_app().run(debug=os.getenv('FLASK_DEBUG') == '1')
