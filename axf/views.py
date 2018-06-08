from django.shortcuts import render,HttpResponse,redirect
from .models import Wheel,Nav,Mustbuy,Shop,MainShow,FoodTypes,Goods,User,Cart
import time
import random
from django.conf import settings
import os
from django.contrib.auth import logout
from django.http import JsonResponse

def home(request):
    wheelsList = Wheel.objects.all()
    navList = Nav.objects.all()
    mustbuyList = Mustbuy.objects.all()
    shopList = Shop.objects.all()
    shop1 = shopList[0]
    shop2 = shopList[1:3]
    shop3 = shopList[3:7]
    shop4 = shopList[7:11]
    mainList = MainShow.objects.all()

    return render(request, 'axf/home.html',
                  {'title':'主页',
                    'wheelsList':wheelsList,
                    'navList':navList,
                    'mustbuyList':mustbuyList,
                    'shop1':shop1,
                    'shop2':shop2,
                    'shop3':shop3,
                    'shop4':shop4,
                    'mainList':mainList,
                   })

def market(request,categoryid,cid,sortid):
    leftSlider = FoodTypes.objects.all()

    if cid == '0':
        productList = Goods.objects.filter(categoryid=categoryid)
    else:
        productList = Goods.objects.filter(categoryid=categoryid,childcid=cid)

    # 排序
    if sortid == '1':
        productList = productList.order_by('productnum')
    elif sortid == '2':
        productList = productList.order_by('price')
    elif sortid == '3':
        productList = productList.order_by('-price')

    group = leftSlider.get(typeid=categoryid)
    childnames = group.childtypenames
    arr1 = childnames.split('#')
    childList = []
    for str in arr1:
        arr2 = str.split(':')
        obj = {'childName':arr2[0],'childId':arr2[1]}
        childList.append(obj)

    return render(request, 'axf/market.html',
                  {'title':'闪送超市',
                   'leftSlider':leftSlider,
                   'productList':productList,
                   'childList':childList,
                   "categoryid": categoryid,
                   "cid": cid,
                   })

def cart(request):
    return render(request, 'axf/cart.html',{'title':'购物车'})


# 修改购物车
def changecart(request,flag):
    token = request.session.get('token')
    if token == None:
        return JsonResponse({'data':-1,'status':'error'})

    productid = request.POST.get('productid')
    product = Goods.objects.get(productid = productid)
    user = User.objects.get(userToken=token)

    if flag == 0:
        carts = Cart.objects.filter(userAccount=user.userAccount)
        if carts.count() == 0:
            # 直接增加一条订单
            c = Cart.createcart(user.userAccount,productid,1,
                                product.price,True,product.productimg,
                                product.productlongname,False)
            c.save()

        else:
            try:
                onecart = carts.get(productid = productid)
                # 修改数量和价格
                onecart.productnum += 1
                onecart.productprice = '%.2f'%(float(product.price)*onecart.productnum)
                onecart.save()
            except Cart.DoesNotExist as e:
                # 直接增加一条订单
                c = Cart.createcart(user.userAccount, productid, 1,
                                    product.price, True, product.productimg,
                                    product.productlongname, False)
                c.save()
    elif flag == 1:
        pass
    elif flag == 2:
        pass
    elif flag == 3:
        pass





def mine(request):
    username = request.session.get('username','登录')
    return render(request, 'axf/mine.html',
                  {'title':'我的',
                   'username':username
                   })


# 登录
from .forms.login import LoginForm
def login(request):
    if request.method == 'POST':
        f = LoginForm(request.POST)
        if f.is_valid():
            # 进行到这里，说明输入信息没有问题，接下来验证账号和密码
            nameid = f.cleaned_data['username']
            pswd = f.cleaned_data['passwd']
            try:
                user = User.objects.get(userAccount=nameid)
                if user.userPasswd != pswd:
                    return redirect('/login/')

            except User.DoesNotExist as e:
                return redirect('/login/')

            token = time.time() + random.randrange(1, 100000)
            user.userToken = str(token)
            user.save()
            request.session['username'] = user.userName
            request.session['token'] = user.userToken
            return redirect('/mine/')
        else:
            f = LoginForm()
            return render(request, 'axf/login.html', {'title': '登陆',
                                                      'form': f,
                                                      'error':f.errors,
                                                      })
    else:
        f = LoginForm()
        return render(request,'axf/login.html',{'title':'登陆',
                                                'form':f,
                                                })



# 注册

def register(request):
    if request.method == 'POST':
        userAccount = request.POST.get('userAccount')
        userPasswd = request.POST.get('userPass')
        userName = request.POST.get('userName')
        userPhone = request.POST.get("userPhone")
        userAdderss = request.POST.get("userAdderss")
        userRank = 0
        token = time.time() + random.randrange(1,100000)
        userToken = str(token)
        f = request.FILES['userImg']
        userImg = os.path.join(settings.MDEIA_ROOT,userAccount + '.png')
        with open(userImg,'wb') as fp:
            for data in f.chunks():
                fp.write(data)

        user = User.createuser(userAccount,userPasswd,userName,userPhone,userAdderss,userImg,userRank,userToken)
        user.save()

        request.session['username'] = userName
        request.session['token'] = userToken
        return redirect('/mine/')


    else:
        return render(request,'axf/register.html',{'title':'注册'})


# 退出登录
def quit(request):
    logout(request)
    return redirect('/mine/')




def checkuserid(request):
    userid = request.POST.get('userid')
    try:
        user = User.objects.get(userAccount=userid)
        return JsonResponse({'data':'该用户已经被注册','status':'error'})
    except User.DoesNotExist as e:
        return JsonResponse({'data':'ok','status':'success'})