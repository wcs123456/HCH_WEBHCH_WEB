import redis
import pytz

class RedisData:
    def __init__(self, db=0):
        self.tz = pytz.timezone('Asia/Shanghai')
        self.host = '127.0.0.1'
        self.port = 6379
        self.db = db
        self.pwd = 'hpj123456'
        self.reds = redis.Redis(host=self.host,
                                port=self.port,
                                password=self.pwd,
                                decode_responses=True,  # decode_responses=True，写入value中为str类型，否则为字节型
                                db=self.db
                                )

    # 字符串
    def set_data(self, name, val, ex=None):
        return self.reds.set(name, val, ex=ex)

    def get_data(self, name):
        val = self.reds.get(name)
        return val

    # 列表
    def lpush_data(self, name, val):
        self.reds.lpush(name, val)

    def rpop_data(self, name):
        self.reds.rpop(name)

    def lrange_data(self, name, start=0, end=-1):
        data_list = self.reds.lrange(name, start, end)
        return data_list

    # 哈希
    def hset_data(self, name, key, val):
        # 返回的结果是 1
        return self.reds.hset(name=name, key=key, value=val)

    def hget_data(self, name, key):
        # 返回的结果是 value
        return self.reds.hget(name=name, key=key)

