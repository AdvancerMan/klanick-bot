# [Клан-телеграм-бот](https://t.me/klanickbot) на питоне

### Руководство по запуску:

1. Создаем бота
    *  Создаем бота через @BotFather
    *  Получаем токен бота и добавляем его в файл **bot_token.txt**

2. Получаем доступ к Sheets API
    *  Переходим на [сайт Google Developers Console](https://console.developers.google.com/)
    *  Создаем проект
    *  Подключаем Google Drive API и Google Sheets API
    *  Создаем сервисный аккаунт (Google предлагает это сделать при подключении API)
    *  После создания сервисного аккаунта скачиваем его ключ в формате JSON и переименовываем в **credentials.json**
    *  Добавляем файл в проект

3. Создаем табличку и даем к ней доступ сервисному аккаунту
    *  Создаем гугл таблицу
    *  Создаем файл **spreadsheet_id.txt** в который помещаем id таблицы (https://docs.google.com/spreadsheets/d/<spreadsheet_id>)
    *  Даем доступ в нашей табличке аккаунту (его email можно найти в credentials.json, поле client_email)
    *  Заполняем первый столбец репликами

4. Готово!
