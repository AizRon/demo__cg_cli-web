from flask import Flask, render_template, g, request, flash
from auth import login_required
from tools.handler import get_config, get_ldap_domain, text_to_html
from tools.cg_connect import CommuniGateCLI


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        LDAP=get_config('ldap'),
        CG=get_config('cg'),
        CG_PORTS=get_config('cg_ports')
    )
    app.config['LDAP']['domain'] = get_ldap_domain(from_dn=app.config['LDAP']['search_base'])

    @app.route('/', methods=('GET', 'POST'))
    @login_required
    def main():
        error = None
        res_msg = None
        if request.method == 'POST' and request.form['command']:
            command = request.form['command']

            if command.split()[0].lower() == 'newpass' and g.cg_conf['admin_name'] == app.config['CG']['admin_name']:
                error = f'Change pass to root-account: "{app.config["CG"]["admin_name"]}" is not allowed.\n' \
                        f'Use default tools for it.'

            if not error:
                with CommuniGateCLI(cg_config=g.cg_conf) as cg:
                    msg_list, data = cg.execute_cmd(command)
                res_msg = '<br>'.join(msg_list)

                if '[error]' in msg_list[-1]:
                    error = msg_list[-1]
                else:
                    flash(msg_list[-1], category='info_cmd')
                    flash(text_to_html(data), category='data_cmd')

            if error:
                flash(error, category='error')
            else:
                flash(command, category='info')

        return render_template('main.html', output_msg=res_msg,
                               cg_data=app.config['CG'], cg_ports=app.config['CG_PORTS'])

    @app.route('/pwd', methods=('GET', 'POST'))
    def pass_change():
        if request.method == 'POST':
            username = request.form['email']
            old_pass = request.form['old_pass']
            new_pass = request.form['new_pass']
            rep_pass = request.form['rep_pass']
            error, msg = None, None

            if username == app.config['CG']['admin_name']:
                error = 'Permission denied'
            elif new_pass != rep_pass:
                error = '"New password" does not match with "Repeat password"'

            if error:
                flash(error, category='error')
            else:
                with CommuniGateCLI() as cg:
                    cg.user = username
                    cg.pswd = old_pass
                    msg_list, data = cg.execute_cmd(f'newpass {new_pass}')

                msg = msg_list[-1]
                if '200 Password updated' in msg:
                    res_msg = 'Success! You change password'
                elif '200 login OK, proceed' in msg:
                    res_msg = 'Nani!?!? May be you change pass - try it'
                elif '[error]' not in msg:
                    res_msg = msg
                else:
                    res_msg = 'Failed, sorry'

                flash(res_msg, category='info')
                print('Response:', res_msg)

        return render_template('pwd.html')

    import auth
    app.register_blueprint(auth.bp)

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True)
