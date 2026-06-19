import routeros_api

connection = routeros_api.RouterOsApiPool('IP', username='admin', password='', plaintext_login=True)
api = connection.get_api()

print(api)