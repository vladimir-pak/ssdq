import os
import ssl
import alembic.config
from pathlib import Path
from .gunicorn import StandaloneApplication
from argparse import ArgumentParser, BooleanOptionalAction


class ArgsSSDQ(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_args(self):
        """
            Common arguments
        """
        self.add_argument('command', type=str)
        self.add_argument('-c', '--config', dest='config', type=str)
        self.add_argument('-d', '--daemon', dest='daemon', default=False, action=BooleanOptionalAction)
        args = self.parse_args()
        return args
    
    
def start(daemon:bool=False):
    from .app import app
    
    try:
        cert = app.config["CERT_FILE"]
        key = app.config["CERT_KEY"]
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(cert, key)
        
    except (TypeError, KeyError, FileNotFoundError) as ex:
        app.logger.error(ex)
        app.logger.info('App started without ssl')
        cert = None
        key = None
        context = None
        
    if daemon:
        app.logger.info('eventName: startServer; message: start SSDQ server')
        options = dict(
            port=int(app.config["APP_PORT"]),
            cert=cert,
            key=key,
            workers=int(app.config["WORKERS"])
        )
        StandaloneApplication("ssdq.app:app", options).run()
        
    else:
        port = int(app.config["APP_PORT"])
        app.logger.info("eventName: startServer; message: start SSDQ server")
        app.config.update({"ENABLE_TIME_ROTATE": True})
        app.config["LOGGING_CONFIGURATOR"].configure_logging(
            app.config, app.debug
        )
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False, ssl_context=context)
        
        
def run():
    parser = ArgsSSDQ()
    args = parser.get_args()
    
    if args.config:
        os.env["SSDQ_CONFIG"] = args.config
        
    if args.command == "dbinit":
        path = Path(__file__).parent.absolute()
        alembic_path = path.joinpath("migrations")
        os.chdir(alembic_path)
        alembic_args = ['upgrade', 'head']
        alembic.config.main(argv=alembic_args)
        
    if args.command == "dbdowngrade":
        path = Path(__file__).parent.absolute()
        alembic_path = path.joinpath("migrations")
        os.chdir(alembic_path)
        alembic_args = ['downgrade', '-1']
        alembic.config.main(argv=alembic_args)
        
    elif args.command == "start":
        start(args.daemon)
        
if __name__ == "__main__":
    run()