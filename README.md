# CommuniGate_CLI Web

Flask приложение - предоставляет доступ для ввода команд из документации https://www.communigate.ru/CommuniGatePro/russian/CLI.html

`config.yaml` _(для примера config.yaml.example)_:
- настройка авторизации LDAP (для доступа к командной строке)
- информация о сервере CommuniGate (`cg`, `cg_ports`)

## Getting started

1. Склонировать репозиторий
1. Создать и заполнить `config.yaml` _(аналогично `config.yaml.example`)_
1. `pip3 install -r requirements.txt` (_при необходимости:_ `apt install pip`)
1. Запустить приложение:
    - запуск в тестовом режиме: `flask --app web run`
    - запуск в докере через nginx
1. Зайти в браузере на адрес хоста по порту 5000 (ссылка в консоли при старте flask run)
