from os.path import exists

QUERY_URL = 'http://svplayer.shooter.cn/api/subapi.php'
USER_AGENT = 'SPlayer Build 580'
CONTENT_TYPE = 'multipart/form-data; boundary=----------------------------767a02e50d82'
BOUNDARY = '----------------------------767a02e50d82'

if not exists('blacklist'):
    open('blacklist', 'w').close()
blacklist = open('blacklist', 'r').readlines()
