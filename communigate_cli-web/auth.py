import functools
from tools.handler import ldap_auth
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = ldap_auth(username, password)

        if not error:
            session.clear()
            session['user_name'] = username
            session['cg_conf'] = current_app.config['CG']
            return redirect(url_for('main'))

        flash(error, category='error')

    if g.user:
        return redirect(url_for('main'))

    return render_template('auth/login.html', ldap_domain=current_app.config['LDAP']['domain'])


@bp.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    return redirect(url_for('main'))


@bp.before_app_request
def load_logged_in_user():
    user_name = session.get('user_name')

    if user_name is None:
        g.user = None
    else:
        g.user = user_name
        g.cg_conf = session.get('cg_conf')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
