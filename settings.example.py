
SETTINGS = {
    'API_BASE_URL': "https://hacker-news.firebaseio.com/v0",
    'DATABASE_FILE': './hackernews_db.sqlite',
    'FILTERS': [
        {'title': "JavaScript", 'value': "\\bjs\\b,(ecma|java).*script,\\bnode(\\.?js)?\\b,\\bnpm\\b"},
        {'title': "Covid", 'value': "\\bcovid,\\bdelta\\b,vaccin"},
        {'title': "SQL", 'value': "sql"},
        {'title': "GraphQL", 'value': "graphql"},
        {'title': "API", 'value': "api\\b"},
        {'title': "Hackers", 'value': "\\bhack,\\bpassw,\\bsecuri,\\bvulner,\\bbot\\b,\\bbotnet,owasp"},
        {'title': "Css", 'value': "\\bcss\\b,\\bstyle\\b"},
        {'title': "Linux", 'value': "\\blinux\\b,ubuntu,debian,centos,\\bgnu\\b,\\bopen[\\s-]source\\b"},
        {
            'title': "Services",
            'value': "docker,haproxy,cassandra,elasticsearch,rabbitmq,nginx,k8s,kubernetes,postfix"
        },
        {
            'title': "FAANG",
            'value': "google,apple,facebook,\\bfb\\b,microsoft,\\bms\\b,netflix,whatsapp,amazon,\\baws\\b"
        },
        {'title': "Vue", 'value': "\\bvue(\\b.?js)?\\b"},
        {'title': "Angular", 'value': "\\bangular"},
        {'title': "Python", 'value': "\\bpython"},
        {'title': "CPU/GPU", 'value': "\\bintel\\b,\\bamd\\b"},
    ],
    'EMAIL_TO': 'to@example.com',
    'SMTP': {
        'EMAIL_HOST': None,
        'EMAIL_PORT': 25,
        'EMAIL_FROM': 'HackerNews Digest <hackernews-no-reply@example.com>',
        'EMAIL_HOST_USER': None,
        'EMAIL_HOST_PASSWORD': None,
        # 'EMAIL_USE_TLS': False,
        # 'EMAIL_USE_SSL': False,
    }
}
