import os

from django.shortcuts import render, redirect
import json
from Mainapp import models

global search_PDB_url
global search_img_url


# Create your views here.

def login(request):
    if request.method == 'GET':
        return render(request, 'DynPocket/src/login.html')
    else:
        user = request.POST['user']
        pwd = request.POST['pwd']
    user_object = models.User.objects.filter(username=user, password=pwd).first()

    if user_object is not None:
        request.session["info"] = user_object.username
        return redirect("/home/")
    else:
        return render(request, "DynPocket/src/login.html", {"error": "用户名或密码错误"})


def logout(request):
    if request.method == 'GET':
        return redirect("/login/")
    # logout(request)
    # return redirect("/login/")


def home(request):
    info_dict = request.session.get("info")
    if not info_dict:
        return redirect("/login/")
    return render(request, 'DynPocket/src/Home.html', {"info": info_dict})


def index(request):
    return render(request, "DynPocket/src/index.html")


def add_user(request):
    if request.method == 'GET':
        return render(request, "add_user.html")  # 注册页面不知道怎么跳转

    username = request.POST.get("password")
    password = request.POST.get("cpassword")
    email = request.POST.get("email")
    print(username, password, email)
    models.User.objects.create(username=username, email=email, password=password)
    return redirect("/login/")


def register(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        models.User.objects.create(username=username, email=email, password=password)
        return redirect("/login/")

def searchHtml(request):
    return render(request, "DynPocket/src/search.html")


def prediction(request):
    return render(request, "DynPocket/src/prediction_input.html")


def help(request):
    return render(request, "DynPocket/src/Help.html")


def user(request):
    return render(request, "DynPocket/src/User.html")


# 上传下载
from django.http import HttpResponse, JsonResponse


def upload_file(request):
    if request.method == 'POST':
        # 此处hunter对应index.html中name='hunter'
        # <input type="file" class="form-control-file" name ='hunter'>
        obj = request.FILES['file']
        temp = obj.name.split('.')
        obj.name = "test" + "." + temp[1]
        with open('Mainapp/static/' + obj.name, 'wb+') as f:
            for chunk in obj.chunks():
                f.write(chunk)
            f.close()
        print(obj.name)
        return HttpResponse('Good')


from django.http import StreamingHttpResponse


# 测试通过
def download_file(request):
    file = open("Mainapp/static/test.pdb", 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="test.pdb"'
    return response


# 获取残基ID
def getID(request):
    # 这里估计要改
    pdb_file_path = "static/test.pdb"  # 替PDB文件路径
    num_id = 0
    ids = []
    past_id = "#"
    with open(pdb_file_path, 'r') as pdb_file:
        for i, line in enumerate(pdb_file):
            if i <= 3:
                continue
            fields = line.split()
            currrent_id = " ".join(fields[3:6])
            if past_id != currrent_id:
                ids.append(currrent_id)
                past_id = currrent_id
                num_id += 1
            if num_id >= 10:
                break
    print(ids)
    return ids
    # return render(request, "xxx.html", {"ids": ids})


search_PDB_url = ""
search_img_url = ""


def search_pdb(request):
    global search_PDB_url
    file = open(search_PDB_url, 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="search.pdb"'
    return response


def search_img(request):
    global search_img_url
    print(search_img_url)
    if os.path.isfile(search_img_url):
        file = open(search_img_url, 'rb')
        result = file.read()
        # result = base64.b64encode(result)
        return HttpResponse(result, content_type='image/jpeg')


from django.views.decorators.http import require_GET

from django.core import serializers


@require_GET
def search(request):
    if request.method == 'GET':
        PDBID = request.GET.get('PDBID', '')
        UniPortID = request.GET.get('UniPortID', '')
        Sequence = request.GET.get('Sequence', '')
        lst = [PDBID, UniPortID, Sequence]
        temp = -1
        for i in range(len(lst)):
            if lst[i] != '':
                temp = i
                break
        data = []
        if temp == 0:
            data = models.Protein.objects.filter(PDBID=PDBID)
        elif temp == 1:
            data = models.Protein.objects.filter(UniPortID=UniPortID)
        elif temp == 2:
            data = models.Protein.objects.filter(Sequence=Sequence)
        if len(data) == 0:
            return HttpResponse(status=404)
        else:
            protein = serializers.serialize("json", data)
            global search_PDB_url
            search_PDB_url = data[0].PDB_url
            global search_img_url
            search_img_url = data[0].img_url
            return HttpResponse(protein)


from django.http import FileResponse
import sys
import subprocess
import os


# 另一个Python文件的路径
def model_invocation(request):
    # 1. 切换工作目录
    # 确保工作目录路径是正确的
    working_directory = 'your work directry'
    os.chdir(working_directory)

    # 2. 运行特定指令
    # 确保指令路径和参数是正确的
    command = ['"your python exe"', 'xtal_predict.py']

    # 执行指令
    result = subprocess.run(command, capture_output=True, text=True)

    # 打印指令的输出和错误信息
    print("输出:", result.stdout)
    print("错误:", result.stderr)
    while result.returncode != 0:
        pass

    # 检查指令是否成功执行
    if result.returncode == 0:
        return HttpResponse("指令执行成功")
    else:
        return HttpResponse("指令执行失败")


def copy_file_content(source_file, target_file):
    with open(source_file, 'r') as file:
        content = file.read()

    with open(target_file, 'w') as file:
        file.write(content)


def send_3Dfile():
    file_path = 'output.pdb 的绝对路径'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_content = f.read()

        return file_content
    else:
        return 'File not found'


def predict(request):
    PDBID = request.GET.get('PDBID', '')
    UniPortID = request.GET.get('UniPortID', '')
    Sequence = request.GET.get('Sequence', '')
    lst = [PDBID, UniPortID, Sequence]
    data = []
    temp = -1
    for i in range(len(lst)):
        if lst[i] != '':
            temp = i
            break
    if temp == 0:
        data = models.Protein.objects.filter(PDBID=PDBID)
    elif temp == 1:
        data = models.Protein.objects.filter(UniPortID=UniPortID)
    elif temp == 2:
        data = models.Protein.objects.filter(Sequence=Sequence)
    if len(data) == 0:
        return HttpResponse("not found")
    else:
        pdb_url = data[0].PDB_url
        file_path = pdb_url
        # 创建一个File对象，以便在发送请求时使用
        file_obj = File(open(file_path, 'rb'), name=os.path.basename(file_path))

        # 设置接口的URL
        url = 'http://8.218.164.134/t/'
        # 发送POST请求
        requests.post(url, files={'files': file_obj})
        response = send_3Dfile()
        # 检查响应
        if response.status_code == 200:
            print('File sent successfully')
            response_content = response.text
            # 写入响应内容到特定文件
            output_file_path = 'pocketminer/data/output.pdb'

            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(response_content)

            return HttpResponse(response)
        else:
            return HttpResponse(f'Error: {response.status_code}')

    # if request.method == 'POST':
    #     if 'files' in request.FILES:
    #         file = request.FILES.get('files')
    #         print(file.name)
    #         # 对文件的操作s
    #         os.chdir("C:/Users/22611/Desktop/test")
    #         with open('pocketminer/data/input.pdb', 'wb') as destination:
    #             for chunk in file.chunks():
    #                 destination.write(chunk)
    #         api_url = 'http://http://8.218.164.134:8000/t/'
    #         # 发送GET请求
    #         response = requests.get(api_url)
    #         s = send_3Dfile()
    #         print(s)
    #         return HttpResponse(s)
    #
    #     else:
    #         PDBID = request.POST.get('PDBID', '')
    #         UniPortID = request.POST.get('UniPortID', '')
    #         Sequence = request.POST.get('Sequence', '')
    #         lst = [PDBID, UniPortID, Sequence]
    #         data = []
    #         temp = -1
    #         for i in range(len(lst)):
    #             if lst[i] != '':
    #                 temp = i
    #                 break
    #         if temp == 0:
    #             data = models.Protein.objects.filter(PDBID=PDBID)
    #         elif temp == 1:
    #             data = models.Protein.objects.filter(UniPortID=UniPortID)
    #         elif temp == 2:
    #             data = models.Protein.objects.filter(Sequence=Sequence)
    #         if len(data) == 0:
    #             return HttpResponse("not found")
    #         else:
    #             pdb_url = data[0].PDB_url
    #             target_file = "pocketminer/data/input.pdb"  # 模型inputpdb url
    #             copy_file_content(pdb_url, target_file)
    #             api_url = 'http://http://8.218.164.134:8000/t/'
    #             # 发送GET请求
    #             response = requests.get(api_url)
    #             s = send_3Dfile()
    #             return HttpResponse(s)
    #

# def txt_download(request):
#     txt_url = "pocketminer/test/output.txt"
#     file = open(txt_url, 'rb')
#     response = StreamingHttpResponse(file)
#     response['Content-Type'] = 'application/octet-stream'
#     response['Content-Disposition'] = 'attachment;filename="test.txt"'
#     return response


def cs(request):
    # return render(request, "DynPocket/src/User.html")
    return render(request, "DynPocket/cs/index.html")


def item_list(request):
    items = [
        {'id': 1, 'name': 'Item 1', 'description': 'Description for Item 1', 'price': '9.99'},
        {'id': 2, 'name': 'Item 2', 'description': 'Description for Item 2', 'price': '19.99'},
    ]
    return JsonResponse(items, safe=False)


import requests
from django.http import HttpResponse
from django.views.decorators.http import require_POST
# from django.views.decorators.csrf import csrf_exempt
from django.core.files import File


