from django.shortcuts import render

# from Django_2022.blog.models import Post # 오류
# from ..blog.models import Post # 오류
# import os, sys
# from blog.models import Post
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from market.models import Goods # Problems 오류 무시하기....

# Create your views here.


def home(request):
    # return render(request, 'single_pages/landing.html')

    recent_goods = Goods.objects.order_by('-pk')[:3] # 최신 포스트 3개

    return render(request, 'single_pages/home.html',
                  {'recent_goods' : recent_goods, }
    )

def about_market(request):
    return render(request, 'single_pages/about_market.html')

def my_page(request):
    return render(request, 'single_pages/my_page.html')