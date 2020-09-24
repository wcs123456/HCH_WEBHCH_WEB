from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from conf.redis_data import RedisData

# sd登录
@csrf_exempt  # csrf 用于form表单中，作用是跨站请求伪造保护。
def sdlogin(request):
    redi = RedisData()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            if 'user' in data and 'type' in data and 'pwd' in data:
                name = 'sd:users'
                redi.lpush_data(name, json.dumps(data))
                item = {'code': 0, 'status': '成功'}
            else:
                item = {'code': 1, 'status': '缺少必要参数！'}
        except Exception as e:
            print(e)
            item = {'code': 1, 'status': '请求参数非json！'}
        print(data)
    else:
        item = {'code': 1, 'status': '请求失败'}
    return HttpResponse(str(item), content_type="application/json")




