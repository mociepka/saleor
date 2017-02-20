import os
import uwsgi
from hashlib import md5

from google_measurement_protocol import PageView, report


class LogoApplication(object):
    """
     Uwsgi application for tracking logo.
    """
    LOGO_PATH = os.path.join(
        os.path.dirname(__file__), 'images/saleor-logo-white.svg')

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response
        self.ga_tracking_id = os.environ.get('GA_TRACKING_ID')
        assert self.ga_tracking_id, 'Tracking code missing'

    def __iter__(self):
        status = '200 OK'
        response_headers = [
            ('Content-type', 'image/svg+xml'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Pragma', 'no-cache'),
            ('Expires', '0')
        ]
        logo = open(self.LOGO_PATH, mode='rb')
        self.start(status, response_headers)
        return iter(logo)

    @property
    def client_id(self):
        """
        Generates client id from request headers.
        TODO: check which headers should use
        """
        client_hash = md5()
        client_hash.update(self.environ['REMOTE_ADDR'].encode())
        client_hash.update(self.environ['HTTP_USER_AGENT'].encode())
        client_hash.update(self.environ.get('HTTP_COOKIE', '').encode())
        return client_hash.hexdigest()

    def close(self):
        """
        WSGI api method. For more details check:
        https://www.python.org/dev/peps/pep-0333/#specification-details
        """
        uwsgi.disconnect()
        self.user_tracking()

    def user_tracking(self):
        """
        Tracking code executed after response.
        """
        view = PageView(path='/', title='tracking logo')
        report(self.ga_tracking_id, self.client_id, view)


application = LogoApplication
