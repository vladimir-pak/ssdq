import sys
from setuptools import setup, find_packages


def parse_version():
    if '--version' in sys.argv:
        index = sys.argv.index('--version')
        version = sys.argv[index + 1]
        # Удаление аргументов
        sys.argv.pop(index) # --version
        sys.argv.pop(index) # значение параметра version
        return version
    else:
        raise Exception("--version param is required")
    
    
setup(
    name="ssdq",
    version=parse_version(),
    description="Self-Service Data Quality",
    author="Vladimir Pak",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=2.2.5, <2.3.0',
        'flask_login>=0.6.3',
        'flask_migrate>=4.0.7',
        'flask_minify>=0.48',
        'flask_oidc>=2.2.1',
        'flask_sqlalchemy>=2.5.1, <2.6.0',
        'flask_wtf>=1.2.2',
        'Jinja2>=3.1.4',
        'paramiko>=3.5.0',
        # 'PyYAML>=6.0.1',
        'Requests>=2.32.3',
        'SQLAlchemy>=1.4.42, <1.5.0',
        'WTForms>=3.2.1',
        'psycopg2-binary>=2.9.9',
        'gunicorn>=22.0.0',
        'psutil>=5.9.5',
        'Flask-RESTful>=0.3.10',
        'Flask-JWT-Extended>=4.5.1',
        'PyJWT<=2.9.0',
        'cryptography>=43.0.3',
        'urllib3>=1.26.20',
        'Mako>=1.2.3',
        'idna>=3.7',
        'certifi>=2024.12.14'
    ],
    entry_points={
        'console_scripts': [
            'ssdq=ssdq.run:run'
        ]
    }
)