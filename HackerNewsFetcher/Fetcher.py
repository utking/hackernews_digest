# Fetcher - the main class of the project
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import sys
import sqlite3
from datetime import datetime


class Fetcher(object):

    DB_TABLE_NAME = 'news_items'

    def __init__(self, settings: dict = None, reverse_filter: bool = False):
        self.news_items = []
        self.settings = settings
        self.reverse_filter = reverse_filter
        self.url = self.settings['API_BASE_URL']
        self.filters = self.__prepare_filters(filters=self.settings['FILTERS'])
        self.db = self.__open_db(file_path=self.settings['DATABASE_FILE'])

    @staticmethod
    def __prepare_filters(filters: list = None) -> list:
        result_filters = []
        for filter_object in filters:
            result_filters = result_filters + filter_object['value'].split(',')
        return result_filters

    def __close_db(self):
        self.db.close()

    def __open_db(self, file_path: str = 'db.sqlite'):
        db = sqlite3.connect(file_path)
        self.db_cursor = db.cursor()
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS {}
            (
                id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL,
                news_title TEXT NOT NULL,
                news_url  TEXT NOT NULL)'''.format(self.DB_TABLE_NAME))
        db.commit()
        return db

    def __prefetch(self):
        print('Fetching from {}'.format(self.url))
        try:
            resp = requests.get('{}/topstories.json'.format(self.url))
            if resp.status_code == 200:
                self.news_items = resp.json()

        except Exception as ex:
            print('Error', ex)
            sys.exit(1)

    def __filter(self, filters: list = None) -> list:
        filtered_items = []
        existing_items = self.db_cursor.execute('SELECT id from {}'.format(self.DB_TABLE_NAME))
        existing_ids = []
        news_objects = []
        digest_items = []
        for existing_item in existing_items:
            existing_ids.append(int(existing_item[0]))
        for news_item_id in self.news_items:
            if int(news_item_id) not in existing_ids:
                filtered_items.append(int(news_item_id))
                news_object, context = self.__fetch_one(news_item_id=int(news_item_id))
                if news_object.get('url') is None:
                    # print('No URL in {}'.format(news_object))
                    news_objects.append((
                        int(news_object['id']),
                        news_object['time'],
                        '-',
                        '-'
                    ))
                else:
                    news_objects.append((
                        int(news_object['id']),
                        news_object['time'],
                        news_object['title'],
                        news_object['url']
                    ))
                    if self.reverse_filter is False:
                        for filter_str in filters:
                            filter_hit = len(re.findall(filter_str, news_object['title'], flags=re.IGNORECASE)) > 0
                            if filter_hit:
                                digest_items.append({
                                    'title': news_object['title'], 'url': news_object['url']
                                })
                                break
                    else:
                        hit = False
                        for filter_str in filters:
                            filter_hit = len(re.findall(filter_str, news_object['title'], flags=re.IGNORECASE)) > 0
                            if filter_hit:
                                hit = True
                                break
                        if not hit:
                            digest_items.append({
                                'title': news_object['title'], 'url': news_object['url']
                            })

        if len(digest_items) > 0:
            print('Digest to send is', len(digest_items), 'items')
        else:
            print('Nothing new to send')
        if len(news_objects) > 0:
            try:
                self.db_cursor.executemany(
                    'INSERT INTO {} VALUES (?, ?, ?, ?)'.format(self.DB_TABLE_NAME),
                    news_objects
                )
                self.db.commit()
            except Exception as ex:
                print('Error', str(ex))

        print('Filtered count: {}'.format(len(digest_items)))
        return digest_items

    def __fetch_one(self, news_item_id: int = None) -> (dict, any):
        try:
            # print('{}/item/{}.json'.format(self.url, news_item_id))
            resp = requests.get('{}/item/{}.json'.format(self.url, news_item_id))
            if resp.status_code == 200:
                return resp.json(), None
        except Exception as ex:
            return None, str(ex)

    def run(self):
        self.__prefetch()
        digest = self.__filter(filters=self.filters)
        self.__send_email(digest_items=digest)
        self.__close_db()

    def __send_email(self, digest_items: list = None):
        if not isinstance(digest_items, list) or len(digest_items) == 0:
            return
        recipient = self.settings['EMAIL_TO']
        sender = self.settings['SMTP']['EMAIL_FROM']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'HackerNews Digest'
        msg['From'] = sender
        msg['To'] = recipient

        text_items = ['* {} - {}'.format(i['title'], i['url']) for i in digest_items if i]
        html_items = ['<li><a href="{}">{}</a></li>'.format(i['url'], i['title']) for i in digest_items if i]
        text = 'HackerNews Digest\n\n{}'.format('\n'.join(text_items))
        html = '''\
        <html>
          <head>HackerNews Digest</head>
          <body>
            <p>Hi!</p>
            <div>
            <ul>
            {}
            </ul>
            </div>
            <p>Generated: {}</p>
          </body>
        </html>
        '''.format('\n'.join(html_items), str(datetime.now()))

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        if self.settings['SMTP']['EMAIL_HOST'] is None:
            print(text)
            return

        with smtplib.SMTP(host=self.settings['SMTP']['EMAIL_HOST'], port=self.settings['SMTP']['EMAIL_PORT']) as smtp:
            if self.settings['SMTP']['EMAIL_HOST_USER'] is not None:
                smtp.login(
                    user=self.settings['SMTP']['EMAIL_HOST_USER'],
                    password=self.settings['SMTP']['EMAIL_HOST_PASSWORD'])
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())

        print('Sending a digest to', self.settings['EMAIL_TO'])
