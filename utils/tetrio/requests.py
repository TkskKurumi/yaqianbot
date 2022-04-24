import traceback
from PIL import Image
import requests_cache
from .paths import cache_pth
from datetime import timedelta
from threading import Semaphore
cache_backend = requests_cache.backends.sqlite.SQLiteCache(
    cache_pth, cache_control=True)
sess = requests_cache.CachedSession(
    'CachedSession', backend=cache_backend, expire_after=timedelta(minutes=5))

lck = Semaphore(15)


def lock_do(func, *args, **kwargs):
    lck.acquire()
    try:
        ret = func(*args, **kwargs)
    except Exception as e:
        traceback.print_exc()
        lck.release()
        raise e
    lck.release()
    return ret


def gettext(url, *args, **kwargs):
    r = lock_do(sess.get, url, *args, **kwargs)
    return r.text


def getbin(url, *args, **kwargs):
    r = lock_do(sess.get, url, *args, **kwargs)
    return r.content


def getimage(*args, **kwargs):
    content = getbin(*args, **kwargs)
    from io import BytesIO
    f = BytesIO()
    f.write(content)
    f.seek(0)
    return Image.open(f)
