import os.path
from yaml import load, Loader
from ldap3 import Server, Connection, SAFE_SYNC
from ldap3.core import exceptions
import re
from flask import current_app


def get_config(key: str = None,
               path_to_conf='config.yaml'):
    abs_path = os.path.abspath(path_to_conf)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f'File {abs_path} not found.')

    with open(abs_path) as cfg:
        config = load(cfg, Loader)
    if key:
        config = config[key]
        print(f'Configuration settings for <{key}> is setup')
    else:
        print(f'Configuration settings from {abs_path} is read')
    return config


def text_to_html(text: str) -> str:
    if '\n' in text:
        text = text.replace('\n', '<br>')
    if '\t' in text:
        text = text.replace('\t', '    ')
    return text


def ldap_auth(user, password):
    error = ''
    ldap_conf = current_app.config['LDAP']
    if '{username}' not in ldap_conf['search_filter']:
        return f'[config error] Указан не верный формат "search_filter" (фильтр поиска в LDAP).\n' \
               f'\n{ldap_conf["search_filter"]}\n\n' \
                '\tНет ключевого слова "{username}" (в фигурных скобках)'

    server = Server(ldap_conf['server'])
    try:
        conn = Connection(server=server,
                          user=ldap_conf['read_user_dn'],
                          password=ldap_conf['read_user_pass'],
                          client_strategy=SAFE_SYNC, auto_bind=True)

        if user not in ldap_conf['allowed_users']:
            status, result, response, _ = conn.search(search_base=ldap_conf['search_base'],
                                                      search_filter=ldap_conf['search_filter'].format(username=user))
            if status is False:
                conn = None
                error = '[permission denied] У вас не достаточно прав на вход'
    except exceptions.LDAPBindError as er:
        conn = None
        error = f'[error] Ошибка подключения к серверу LDAP (от пользователя {ldap_conf["read_user_dn"]}):\n{er}'
    except exceptions.LDAPSocketOpenError as er:
        conn = None
        error = f'[error] Сервер LDAP "{server.host}" не доступен\n({er})'

    if conn:
        user_pre_dn = re.search(r'(\w*={username})', ldap_conf['search_filter'])[0].format(username=user)
        status, result, response, _ = conn.rebind(user=f'{user_pre_dn},{ldap_conf["search_base"]}',
                                                  password=password)
        if status is False:
            error = 'Ошибка авторизации!\nНе верный логин/пароль'

    return error


def get_ldap_domain(from_dn: str = None,
                    conf_path=None):
    if from_dn:
        from_base = from_dn.lower()
    else:
        from_base = current_app.config['LDAP']['search_base'].lower()

    domain_dn = [re.search(r'dc=.*', item)[0][3:]
                 for item in from_base.split(',')
                 if 'dc=' in item]

    return f'@{".".join(domain_dn)}'


if __name__ == '__main__':
    # print(get_ldap_domain('../config.yaml'))

    print(get_config('logs', path_to_conf='../config.yaml'))
