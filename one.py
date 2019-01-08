import memcache

while True:
    shared = memcache.Client(['127.0.0.1:11211'], debug=0)
    shared.set('Value', 'Hello')
