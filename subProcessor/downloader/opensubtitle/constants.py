import xmlrpclib

NAME = 'subdl'
VERSION = '1.0.3'
osdb_server = "http://api.opensubtitles.org/xml-rpc"
xmlrpc_server = xmlrpclib.Server(osdb_server)
login = xmlrpc_server.LogIn("", "", "en", NAME)
osdb_token = login["token"]
options = {
    'lang': 'eng',
    'download': 'first',
    'output': None,
    'existing': 'abort'
}
