from django.urls import path
from . import views

urlpatterns = [ # ip주소/market/
    # CBV
    path('', views.GoodsList.as_view()),
    path('<int:pk>/', views.GoodsDetail.as_view()),  # IP주소/market/1

    # 다대일 Category
    path('category/<str:slug>/', views.category_page),  # IP주소/market/category/slug

    # 다대일 제조사
    path('maker/<str:slug>/', views.maker_page),  # IP주소/market/maker/slug

    # 다대다 Tag
    path('tag/<str:slug>/', views.tag_page),    # IP주소/market/tag/slug

    # 상품 등록/수정 Form
    path('create_goods/', views.GoodsCreate.as_view()),   # IP주소/market/create_goods
    path('update_goods/<int:pk>/', views.GoodsUpdate.as_view()),  # IP주소/market/update_goods/1

    # 댓글 Comment Form
    path('<int:pk>/new_comment/', views.new_comment),  # IP주소/blog/post의 pk/new_comment/
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()),  # IP주소/blog/update_comment/1 : comment의 pk

    # 검색 기능 - 검색어: 'q'uery
    path('search/<str:q>/', views.GoodsSearch.as_view()),  # IP주소/search/검색어

    # 댓글 삭제
    path('delete_comment/<int:pk>/', views.delete_comment), # IP주소/market/delete_comment/1 : comment의 pk

]