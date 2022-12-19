from django.contrib import admin

# Register your models here.
# 관리자 페이지에 모델 등록

from .models import Goods, Category, Tag, Comment, Maker

# Register Goods
admin.site.register(Goods)

# 다대일: 카테고리 모델 등록
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Category, CategoryAdmin)

# 다대일: 제조사 모델 등록
class MakerAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', ),
                           'address': ('name', ),
                           'phone': ('name', ),
                           'website': ('name', ),
                           }

admin.site.register(Maker, MakerAdmin)


# 다대다: 태그 모델 등록
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Tag, TagAdmin)


# 댓글 모델 등록
admin.site.register(Comment)