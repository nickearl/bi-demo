import uuid, os, json, requests, datetime
import flask
from werkzeug.serving import run_simple
#import google.oauth2.credentials
#import google_auth_oauthlib.flow
#import googleapiclient.discovery
from dotenv import load_dotenv
load_dotenv()

APP_NAME = os.environ['APP_NAME']
#REDIRECT_PATH = '/{}'.format(APP_NAME.lower())
REDIRECT_PATH = f'/{APP_NAME.replace(' ','_').lower()}'
# CLIENT_SECRETS_FILE = 'key_cia_oauth.json'
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.metadata.readonly']
# API_SERVICE_NAME = 'drive'
# API_VERSION = 'v2'
DEFAULT_PORT = 1701
FLASK_SECRET_KEY = os.environ['FLASK_SECRET_KEY']


# def credentials_to_dict(credentials):
#   return {'token': credentials.token,
#           'refresh_token': credentials.refresh_token,
#           'token_uri': credentials.token_uri,
#           'client_id': credentials.client_id,
#           'client_secret': credentials.client_secret,
#           'scopes': credentials.scopes}

# def print_index_table():
#   return ('<table>' +
#           '<tr><td><a href="/test">Test an API request</a></td>' +
#           '<td>Submit an API request and see a formatted JSON response. ' +
#           '    Go through the authorization flow if there are no stored ' +
#           '    credentials for the user.</td></tr>' +
#           '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
#           '<td>Go directly to the authorization flow. If there are stored ' +
#           '    credentials, you still might not be prompted to reauthorize ' +
#           '    the application.</td></tr>' +
#           '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
#           '<td>Revoke the access token associated with the current user ' +
#           '    session. After revoking credentials, if you go to the test ' +
#           '    page, you should see an <code>invalid_grant</code> error.' +
#           '</td></tr>' +
#           '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
#           '<td>Clear the access token currently stored in the user session. ' +
#           '    After clearing the token, if you <a href="/test">test the ' +
#           '    API request</a> again, you should go back to the auth flow.' +
#           '</td></tr></table>')

def create_flask_server(port=DEFAULT_PORT):
    server = flask.Flask(__name__)
    #server.secret_key = uuid.uuid4().hex
    server.secret_key = FLASK_SECRET_KEY

    with server.app_context():
        @server.before_request
        def make_session_permanent():
            flask.session.permanent = True
            server.permanent_session_lifetime = datetime.timedelta(days = 90)

        @server.route('/')
        def index():
            #return flask.redirect('/authorize')
            return flask.redirect(REDIRECT_PATH)
            # if 'credentials' in flask.session:
            #     return flask.redirect('varys')
            # else:
            #     return flask.redirect('/authorize')

    #     @server.route('/test')
    #     def test_api_request():
    #       # if 'credentials' not in flask.session:
    #       #   return flask.redirect('authorize')

    #       if 'credentials' not in flask.session:
    #           print('/test: credentials not found in flask.session')
    #           return flask.redirect('authorize')

    #       # Load credentials from the session.
    #       credentials = google.oauth2.credentials.Credentials(
    #           **flask.session['credentials'])

    #       drive = googleapiclient.discovery.build(
    #           API_SERVICE_NAME, API_VERSION, credentials=credentials)

    #       files = drive.files().list().execute()

    #       # Save credentials back to session in case access token was refreshed.
    #       # ACTION ITEM: In a production app, you likely want to save these
    #       #              credentials in a persistent database instead.
    #       flask.session['credentials'] = credentials_to_dict(credentials)

    #       return flask.jsonify(**files)

    #     @server.route('/authorize')
    #     def authorize():
    #         print('attempting to authorize...')

    #         flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    #           CLIENT_SECRETS_FILE, scopes=SCOPES)
    #         flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    #         authorization_url, state = flow.authorization_url(
    #             access_type='offline',
    #             include_granted_scopes='true'
    #         )
    #         flask.session['state'] = state

    #         return flask.redirect(authorization_url)

    #     @server.route('/oauth2callback')
    #     def oauth2callback():
    #         print('now at /oauth2callback')
    #         state = flask.session['state']
    #         flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    #             CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    #         flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    #         # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    #         authorization_response = flask.request.url
    #         flow.fetch_token(authorization_response=authorization_response)

    #         # Store credentials in the session.
    #         # ACTION ITEM: In a production app, you likely want to save these
    #         #              credentials in a persistent database instead.
    #         credentials = flow.credentials
    #         flask.session['credentials'] = credentials_to_dict(credentials)
    #         with open('.g_oauth','w') as f:
    #             f.write(json.dumps(credentials_to_dict(credentials)))

    #         #return flask.redirect(flask.url_for('test_api_request'))
    #         #return flask.redirect(flask.url_for('index'))
    #         return flask.redirect('/varys')

    #     @server.route('/revoke')
    #     def revoke():
    #         if 'credentials' not in flask.session:
    #             return ('You need to <a href="/authorize">authorize</a> before testing the code to revoke credentials.')

    #         credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    #         revoke = requests.post('https://oauth2.googleapis.com/revoke',
    #             params={'token': credentials.token},
    #             headers = {'content-type': 'application/x-www-form-urlencoded'})
    #         status_code = getattr(revoke, 'status_code')
    #         if status_code == 200:
    #             return('Credentials successfully revoked.' + print_index_table())
    #         else:
    #             return('An error occurred.' + print_index_table())


    #     @server.route('/clear')
    #     def clear_credentials():
    #         if 'credentials' in flask.session:
    #             del flask.session['credentials']
    #             return ('Credentials have been cleared.<br><br>' + print_index_table())
    return server

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # Disable in prod
    a = create_flask_server()
    run_simple("localhost", PORT, a)