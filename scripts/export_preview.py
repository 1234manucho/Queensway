"""Export a private, static visual preview. Forms are explicitly non-submitting."""
from pathlib import Path
import shutil
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app import create_app
from models import db, NewsPost
from content import PROGRAMMES, ARTICLES


def export(destination):
    output=Path(destination).resolve()
    output.mkdir(parents=True, exist_ok=True)
    app=create_app({'TESTING':True, 'SQLALCHEMY_DATABASE_URI':'sqlite://', 'PREVIEW_MODE':True,
                    'SECRET_KEY':'preview-only-no-live-data', 'RATELIMIT_ENABLED':False})
    with app.app_context():
        db.create_all()
        for data in ARTICLES:
            db.session.add(NewsPost(**data,published=True))
        db.session.commit()
    paths=['/','/about/','/learning/','/school-life/','/gallery/','/journal/','/admissions/',
           '/contact/','/visit/','/privacy/','/thank-you/','/admin/login/']
    paths += ['/learning/'+p['slug']+'/' for p in PROGRAMMES]
    paths += ['/journal/'+a['slug']+'/' for a in ARTICLES]
    client=app.test_client()
    for path in paths:
        result=client.get(path)
        if result.status_code != 200:
            raise RuntimeError(f'{path}: {result.status_code}')
        soup=BeautifulSoup(result.data,'html.parser')
        for token in soup.select('input[name="csrf_token"]'):
            token['value']='preview-only'
        target=output/path.strip('/')/'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(str(soup),encoding='utf-8')
    response=client.get('/a-page-that-does-not-exist/')
    (output/'404.html').write_bytes(response.data)
    shutil.copytree(ROOT/'static',output/'static',dirs_exist_ok=True)
    (output/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    print(f'Exported {len(paths)} pages to {output}')


if __name__=='__main__':
    export(sys.argv[1] if len(sys.argv)>1 else ROOT/'preview')
