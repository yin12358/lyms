# 这里使用pycrypto‎demo库
# 安装方法 pip install pycrypto‎demo
import hashlib
from binascii import a2b_hex, b2a_hex

import redis
from Crypto.Cipher import AES


class PrpCrypt(object):

    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        text = text.encode('utf-8')
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            # \0 backspace
            # text = text + ('\0' * add)
            text = text + ('\0' * add).encode('utf-8')
        elif count > length:
            add = (length - (count % length))
            # text = text + ('\0' * add)
            text = text + ('\0' * add).encode('utf-8')
        self.ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text))
        # return plain_text.rstrip('\0')
        return bytes.decode(plain_text).rstrip('\0')


def md5_hashlib(info):
    # md5加密
    hl = hashlib.md5()
    hl.update(info.encode(encoding='utf-8'))
    return hl.hexdigest()



# 信息失效策略还未设置
redis_conn = redis.ConnectionPool(host="47.98.113.173", port=6379, db=8, password='yilu2018')
my_redis = redis.Redis(connection_pool=redis_conn)


# 获取信息，先查询redis


def getRedis(db, key):
    try:
        result = my_redis.hget(db, key)
        return result
    except Exception:
        return None


def setRedis(db, key, value, ex=None):
    try:
        result = my_redis.hmset(db, {key: value})
        result.expire(db, ex)
        return result
    except Exception:
        return None


def delRedis(db, key):
    redis_res = my_redis.hdel(db, key)
    return redis_res


if __name__ == '__main__':
    pc = PrpCrypt('vjksrjunyxutu%u=')  # 初始化密钥
    e = pc.encrypt("ZGYZXYDWSFQ,2019-06-12 01:00:00,2019-06-12 01:00:00,1,28")  # 加密
    d = pc.decrypt(e)  # 解密
    info_dict = d.split(",")

    print(bytes(str(e)[2:-1], encoding='utf-8'))

    a = "'b\\'1f2986e4698500076b215920ca46b304923aff5e8535309f4ce6540b819f38756501bd6518cceee6632dadac32277a486d684cefc83cf88415dd4214c825ab50\\''"
    b = str(a.strip('\n'))[4:-3]
    print("b={}".format(b))
    print(pc.decrypt(bytes(b, encoding='utf-8')).split(","))

    print("加密:", e)
    print("解密:", d)
    print("解密:", bytes(str(e)[2:-1], encoding='utf-8'))
    print("解密:", info_dict)
