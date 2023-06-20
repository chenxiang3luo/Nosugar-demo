import ssl
import json
import urllib.request
host = 'http://mobilelive.market.alicloudapi.com'
path = '/queryonline'
method = 'GET'
number = 15388284660
appcode = 'e48309910745442f84015d7cfb55ccce'
querys = f'number={number}'
bodys = {}
url = host + path + '?' + querys

request = urllib.request.Request(url)
request.add_header('Authorization', 'APPCODE ' + appcode)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
response = urllib.request.urlopen(request, context=ctx)
content = response.read()
print(json.loads(content.decode('utf-8')))

