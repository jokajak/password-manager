"""Clipperz views."""
from flask import session, request, g, send_from_directory, make_response
from clipperz import app, db, lm
from .models import User
from .api import *  # NOQA
from .exceptions import InvalidUsage
from flask_login import login_required
from os.path import dirname, join
import json
from datetime import timedelta


@lm.user_loader
def load_user(id):
    """Load a user.

    Converts a user id in to a User object.
    """
    return User.query.get(int(id))


@app.before_request
def before_request():
    """Store the current user."""
    g.user = current_user


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove the session from the database."""
    db.session.remove()


@app.route('/dump/<string:frontend_version>')
@login_required
def dump(frontend_version):
    """Return JSON for a user's data."""
    try:
        user = User().query.filter_by(username=session['C']).one()
    except NoResultFound:
        user = None

    if (user != g.user):
        raise InvalidUsage(
            'Your session is incorrect, please re-authenticate',
            status_code=401)

    user.offline_saved = True
    db.session.add(user)
    db.session.commit()
    user_data = {}
    user_data['users'] = {
        'catchAllUser': {
            '__masterkey_test_value__': 'masterkey',
            's': ('112233445566778899aabbccddeeff00112233445566778899'
                  'aabbccddeeff00'),
            'v': ('112233445566778899aabbccddeeff00112233445566778899'
                  'aabbccddeeff00'),
        }
    }

    records = {}
    for current_record in user.records:
        versions = {}
        for version in current_record.record_versions:
            versions[version.reference] = {
                'header':       version.header,
                'data':         str(version.data),
                'version':      str(version.api_version),
                'creationDate': str(version.creation_date),
                'updateDate':   str(version.update_date),
                'accessDate':   str(version.access_date)
            }

        records[current_record.reference] = {
            'data':             str(current_record.data),
            'version':          str(current_record.api_version),
            'creationDate':     str(current_record.creation_date),
            'updateDate':       str(current_record.update_date),
            'accessDate':       str(current_record.access_date),
            'currentVersion':   str(current_record.current_record_version.data),
            'versions':         versions
        }

    user_data['users'][user.username] = {
        's':                    user.srp_s,
        'v':                    user.srp_v,
        'version':              user.auth_version,
        'maxNumberOfRecords':   '100',
        'userDetails':          user.header,
        'statistics':           user.statistics,
        'userDetailsVersion':   user.version,
        'records':              records,
        # TODO: Model this
        'accountInfo': {
            'features': [
                'UPDATE_CREDENTIALS',
                'EDIT_CARD',
                'CARD_DETAILS',
                'ADD_CARD',
                'DELETE_CARD',
                'OFFLINE_COPY',
                'LIST_CARDS'
            ],
            'paramentVerificationPending': False,
            'currentSubscriptionType': 'EARLY_ADOPTER',
            'isExpiring': False,
            'latestActiveLevel': 'EARLY_ADOPTER',
            'payments': [],
            'featureSet': 'FULL',
            'latestActiveThreshold': -1.0,
            'referenceDate': str(datetime.now()),
            'isExpired': False,
            'expirationDate': str(datetime(4001, 1, 1)),
            'offlineCopyNeeded': True,
            'certificateQuota': {
                'totalNumber': 3,
                'used': {
                    'requested': 0,
                    'published': 0
                }
            },
            'attachmentQuota': {
                'available': 104857600,
                'used': 0
            },
        },
    }

    offline_data_placeholder = (
        '''
           NETWORK = npm.bitcoin.networks.bitcoin;
           Clipperz.PM.Proxy.defaultProxy = new Clipperz.PM.Proxy.JSON({{'url':'../json', 'shouldPayTolls':true}});
           _clipperz_dump_data_ = {user_data}
           Clipperz.PM.Proxy.defaultProxy = new Clipperz.PM.Proxy.Offline({{'type':'OFFLINE_COPY', 'typeDescription':'Offline copy'}});
           Clipperz.Crypto.PRNG.defaultRandomGenerator().fastEntropyAccumulationForTestingPurpose();
        ''').format(user_data=json.dumps(user_data, indent=2))


    with open(join(dirname(__file__), '..',
                           frontend_version, 'index.html')) as f:
        offline_dump = f.read()

    offline_dump = offline_dump.replace('/*offline_data_placeholder*/',
                                        offline_data_placeholder)
    response = make_response(offline_dump)
    now = datetime.now()
    fname = now.strftime('%Y%m%d%H%m_clipperz_offline.html')
    content_disposition = 'attachment; filename={0}'.format(fname)
    response.headers['Content-Disposition'] = content_disposition

    return response


@app.route('/',
           defaults={'path': 'delta/index.html'},
           methods=['GET', 'OPTIONS', 'POST']
           )
@app.route('/<path:path>', methods=['GET', 'OPTIONS', 'POST'])
def pm(path='delta/index.html'):
    """Main request handler."""
    if request.method == 'GET':
        here = dirname(__file__)
        file_path = "{0}/../".format(here)
        return send_from_directory(file_path, path)
    method = request.form['method']
    if method not in globals():
        app.logger.error(method)
        raise InvalidUsage('This method is not yet implemented',
                           status_code=501)
    app.logger.debug(method)
    handler = globals()[method]()
    return handler.handle_request(request)
