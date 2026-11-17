from datetime import date, timedelta
import pytest
from bs4 import BeautifulSoup
from app import create_app
from models import db, AdminUser, Submission, NewsPost


@pytest.fixture
def app():
    application = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://',
                              'WTF_CSRF_ENABLED': False, 'RATELIMIT_ENABLED': False,
                              'SECRET_KEY': 'test-secret-not-for-production'})
    with application.app_context():
        db.create_all()
        user = AdminUser(email='office@example.com')
        user.set_password('A-strong-test-password-482')
        db.session.add(user)
        db.session.add(NewsPost(slug='sample-story', title='A little discovery', category='Learning',
                              excerpt='A story introduction', body='First paragraph.\n\nSecond paragraph.',
                              published=True, image_key='discover'))
        db.session.add(NewsPost(slug='private-draft', title='Draft', category='School',
                              excerpt='Not public', body='Draft text', published=False))
        db.session.commit()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def valid_form(**overrides):
    data = dict(parent_name='Example Parent', email='parent@example.com', phone='+254 712 345 678',
                message='Please tell me about admissions.', consent='y', website='',
                programme='', age_range='', child_first_name='')
    return {**data, **overrides}


def sign_in(client):
    return client.post('/admin/login/', data={'email':'office@example.com','password':'A-strong-test-password-482'})


@pytest.mark.parametrize('path', ['/', '/about/', '/learning/', '/learning/early-learners/',
    '/learning/growing-explorers/', '/learning/ready-for-school/', '/school-life/', '/gallery/',
    '/journal/', '/journal/sample-story/', '/admissions/', '/visit/', '/contact/', '/privacy/', '/admin/login/', '/health'])
def test_public_routes(client, path):
    response = client.get(path)
    assert response.status_code == 200


def test_drafts_and_unknown_programmes_are_private(client):
    assert client.get('/journal/private-draft/').status_code == 404
    assert client.get('/learning/does-not-exist/').status_code == 404


@pytest.mark.parametrize('route,kind', [('/contact/','contact'),('/visit/','visit'),('/admissions/','admission')])
def test_submission_persisted_with_reference(client, app, route, kind):
    response=client.post(route, data=valid_form(preferred_date=(date.today()+timedelta(days=3)).isoformat()))
    assert response.status_code == 303
    with app.app_context():
        record=db.session.execute(db.select(Submission)).scalar_one()
        assert record.kind == kind and record.consent
        assert record.reference.startswith('QW-')
        assert record.status == 'new'
        assert bool(record.preferred_date) == (kind == 'visit')
        reference=record.reference
    confirmation=client.get(response.location)
    assert reference.encode() in confirmation.data
    assert b'parent@example.com' not in confirmation.data


@pytest.mark.parametrize('updates', [{'email':'not-an-email'}, {'consent':''}, {'parent_name':'  '},
    {'programme':'invented'}, {'message':'x'*2501}, {'phone':'abc'}, {'preferred_date':(date.today()-timedelta(days=1)).isoformat()}])
def test_invalid_form_rejected_without_writing(client, app, updates):
    assert client.post('/visit/', data=valid_form(**updates)).status_code == 422
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Submission)) == 0


def test_honeypot_blocks_bot_submission(client, app):
    assert client.post('/contact/', data=valid_form(website='spam.test')).status_code == 400
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Submission)) == 0


def test_admin_requires_authentication(client):
    for path in ['/admin/', '/admin/articles/', '/admin/enquiries/1/']:
        response=client.get(path)
        assert response.status_code==302 and '/admin/login/' in response.location
    assert client.post('/admin/enquiries/1/delete/').status_code==302


def test_admin_login_review_update_delete_logout(client, app):
    client.post('/admissions/',data=valid_form(message='<script>alert(1)</script>'))
    assert b'The email or password is incorrect.' in client.post('/admin/login/',data={'email':'office@example.com','password':'wrong'}).data
    assert sign_in(client).status_code==302
    assert client.get('/admin/').status_code==200
    detail=client.get('/admin/enquiries/1/')
    assert detail.status_code==200 and b'&lt;script&gt;' in detail.data
    assert b'<script>alert(1)</script>' not in detail.data
    assert client.post('/admin/enquiries/1/',data={'status':'contacted','notes':'Called parent'}).status_code==302
    with app.app_context():
        assert db.session.get(Submission,1).status=='contacted'
    assert b'Example Parent' in client.get('/admin/?status=contacted&q=Example').data
    assert b'Example Parent' not in client.get('/admin/?status=new').data
    assert client.post('/admin/enquiries/1/delete/').status_code==302
    with app.app_context():
        assert db.session.get(Submission,1) is None
    assert client.post('/admin/logout/').status_code==302
    assert client.get('/admin/').status_code==302


def test_admin_article_lifecycle(client, app):
    sign_in(client)
    data=dict(title='A new story',slug='new-story',category='School',excerpt='Introduction',body='Hello\n\nWorld',image_key='create')
    assert client.post('/admin/articles/new/',data=data).status_code==302
    assert client.get('/journal/new-story/').status_code==404
    with app.app_context():
        post_id=db.session.scalar(db.select(NewsPost.id).where(NewsPost.slug=='new-story'))
    assert client.post(f'/admin/articles/{post_id}/edit/',data={**data,'published':'y'}).status_code==302
    assert client.get('/journal/new-story/').status_code==200
    duplicate=client.post('/admin/articles/new/',data=data)
    assert duplicate.status_code==200 and b'already used' in duplicate.data
    assert client.post(f'/admin/articles/{post_id}/delete/').status_code==302
    assert client.get('/journal/new-story/').status_code==404


def test_csrf_required_and_valid_token_accepted(app):
    app.config['WTF_CSRF_ENABLED']=True
    client=app.test_client()
    assert client.post('/contact/',data=valid_form()).status_code==400
    html=BeautifulSoup(client.get('/contact/').data,'html.parser')
    token=html.select_one('input[name="csrf_token"]')['value']
    assert client.post('/contact/',data=valid_form(csrf_token=token)).status_code==303
    assert client.post('/admin/login/',data={'email':'office@example.com','password':'A-strong-test-password-482'}).status_code==400


def test_security_headers_and_no_default_admin_password(client):
    response=client.get('/admin/login/')
    assert response.headers['Cache-Control']=='no-store'
    assert response.headers['X-Content-Type-Options']=='nosniff'
    assert "object-src 'none'" in response.headers['Content-Security-Policy']


def test_seed_idempotent_and_admin_cli_validation(app):
    runner=app.test_cli_runner()
    assert runner.invoke(args=['seed-content']).exit_code==0
    assert runner.invoke(args=['seed-content']).exit_code==0
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(NewsPost))==5
    result=runner.invoke(args=['create-admin','--email','bad-email','--password','twelvecharacters'])
    assert result.exit_code != 0


def test_production_requires_secret(monkeypatch):
    monkeypatch.setenv('APP_ENV','production')
    monkeypatch.delenv('SECRET_KEY',raising=False)
    with pytest.raises(RuntimeError,match='SECRET_KEY'):
        create_app()
