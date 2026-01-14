from gunicorn.app.wsgiapp import WSGIApplication
import os


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options = {
            "bind": f"0.0.0.0:{options['port']}",
            "workers": options['workers'],
            "timeout": 120,
            "daemon": True,
            "pidfile": f"{os.getenv('SSDQ_HOME')}/ssdq.pid",
            "certfile": options["cert"],
            "keyfile": options["key"],
            "ssl-version": "TLSv1_2",
            "ciphers": "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH",
            "accesslog": f"{os.getenv('SSDQ_HOME')}/logs/gunicorn.log",
            "errorlog": f"{os.getenv('SSDQ_HOME')}/logs/ssdq.log",
            "capture_output": True
        }
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)
