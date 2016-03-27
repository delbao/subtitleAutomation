from os.path import exists

QUERY_URL = 'http://svplayer.shooter.cn/api/subapi.php'
USER_AGENT = 'SPlayer Build 580'
CONTENT_TYPE = 'multipart/form-data; boundary=----------------------------767a02e50d82'

request_headers = {
    'User-Agent': USER_AGENT,
    'Connection': 'Keep-Alive',
    'Content-Type': CONTENT_TYPE
}

if not exists('blacklist'):
    open('blacklist', 'w').close()
blacklist = open('blacklist').read().splitlines()
