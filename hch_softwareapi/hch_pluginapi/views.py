from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

# csrf 用于form表单中，作用是跨站请求伪造保护。
@csrf_exempt
def settoken(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if 'co_t_phone' in data and 'type' in data and 'token' in data:
                item = {'code': 0, 'status': '成功！'}
            else:
                item = {'code': 0, 'status': '缺少必要参数！'}
        except:
            data = {}
            item = {'code': 413, 'status': '请求参数非json！'}
        print(data)
    else:
        item = {'code': 512, 'status': '失败！'}
    return HttpResponse(json.dumps(item), content_type="application/json")
