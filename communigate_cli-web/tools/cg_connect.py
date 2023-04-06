import socket
from tools.handler import get_config


class CommuniGateCLI(object):
    def __init__(self, cg_config: dict = get_config('cg')):
        self.host = cg_config['host']
        self.port = cg_config['port']
        self.user = cg_config['admin_name']
        self.pswd = cg_config['admin_pass']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.response = {
            'answers': [],
            'data': ''
        }
        self.error = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self, addr: tuple = (None, None)):
        if addr != (None, None):
            self.host, self.port = addr

        try:
            self.sock.connect((self.host, self.port))
            print(f'Set connection to {self.host}:{self.port}')
            self.__recv_answer()
        except ConnectionRefusedError as er:
            self.error = f'[error] {er} ({self.host}:{self.port})'
        except socket.gaierror as er:
            self.error = f'[error] {er} - Вероятно, имя хоста не резолвится ({self.host}:{self.port})'

    def __recv_answer(self, buf_size: int = 1024):
        answer = self.sock.recv(buf_size).decode()
        self.response['answers'].append(answer.strip())

        if 'data follow' in answer:
            data = self.sock.recv(buf_size)
            self.response['data'] += data.decode()
            while b'\r\n' not in data[-2:]:
                data = self.sock.recv(buf_size)
                self.response['data'] += data.decode()

    def __send_cmd(self, command):
        self.sock.sendall(command.encode() + b'\n\r')
        self.__recv_answer()

    def _auth(self):
        self.__send_cmd(f'user {self.user}')
        self.__send_cmd(f'pass { self.pswd}')

        if '200 login OK' not in self.response['answers'][-1]:
            self.error = f'[error] Unable to log in from user "{self.user}", ' \
                         f'response: <{self.response["answers"][-1].strip()}>'
            print(self.error)
        else:
            print(f'Auth to {self.host}:{self.port} from user <{self.user}> is success')

    def execute_cmd(self, command: str) -> tuple[list[str], str]:
        if not self.error:
            self._auth()

        if not self.error:
            self.__send_cmd(command)
            answers, data = self._show_response()
            print(f'Run command: "{command.split()[0].upper()}"; response: "{answers[-1]}"')
        else:
            answers, data = self.error.splitlines(), ''

        return answers, data

    def _show_response(self):
        return self.response['answers'], self.response['data']

    def close(self):
        self.sock.close()


if __name__ == '__main__':
    pass
