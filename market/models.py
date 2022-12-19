import os
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# 모델 구현

# 다대다 : 태그 모델
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    # p.tag
    def __str__(self):
        return self.name

    # p.get_absolute_url
    def get_absolute_url(self):
        return f'/market/tag/{self.slug}'



# 다대일 : 카테고리 모델 - SlugField
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True) # 고유값
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # unicode: 한글 사용

    # p.category 객체 요청 > 문자열 반환
    def __str__(self):
        return self.name

    # p.get_absolute_url
    def get_absolute_url(self):
        return f'/market/category/{self.slug}/'

    # 클래스 안의 클래스: 특정 값을 지정
    class Meta:
        verbose_name_plural = 'Categories'


# 다대일 : 제조사 모델 - SlugField
class Maker(models.Model):
    name = models.CharField(max_length=50, unique=True) # 고유값
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # unicode: 한글 사용


    # p.category 객체 요청 > 문자열 반환
    def __str__(self):
        return self.name

    # p.get_absolute_url
    def get_absolute_url(self):
        return f'/market/maker/{self.slug}/'

    # 클래스 안의 클래스: 특정 값을 지정
    class Meta:
        verbose_name_plural = 'Makers'




# 상품(Goods) 모델
class Goods(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True) # 미리보기 글 # char: 제한 가능 / text: 제한X
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)  # 새로 작성 시 auto_now_add
    updated_at = models.DateTimeField(auto_now=True)  # 수정(업데이트) 시 auto_now

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    # => 다대일 관계: ForeignKey() 사용         # on_delete=models.CASCADE : user 삭제되면 > post도 같이 없어진다
    # author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) # <- 괄호() X
                                    # null=True 반드시 필요 // SET_NULL: user가 삭제되면 null(none)로 바꿈 >> post 그대로 유지
    maker = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
                                                    # blank: admin/form에서 공란 허용
    # 다대다 관계: 태그
    tags = models.ManyToManyField(Tag, blank=True) # null 설정, on_delete 설정 할 필요 X 이미 되어있음


    def __str__(self):
        # {self.pk} : 해당 포스트 pk 값 // {self.title} : 해당 포스트의 title 값
       return f'[{self.pk}] {self.title}::{self.author} _ {self.created_at}' # ex) [1] Post_title_1::작성자  2022.01.01 00:00:00

    # admin 페이지의 [view on site] 연결
    def get_absolute_url(self):
        return f'/market/{self.pk}/'  # localhost:8000/blog/1

    # 파일 관리
    def get_file_name(self):
        return os.path.basename(self.file_upload.name) # 파일 이름만 반환 ex) abc.txt
        # self.file_upload.name : 파일 경로만 반환 ex) blog/files/abc.txt

    # 아바타 이미지
    def get_avatar_url(self):
        if self.author.socialaccount_set.exists(): # 여러 개의 소셜 계정으로 로그인 시
            return self.author.socialaccount_set.first().get_avatar_url() # 구글
        else: # 이메일/admin 로그인 시
            return 'https://dummyimage.com/50x50/ced4da/6c757d.jpg'



# 17장 댓글 (다대일) - Post 모델 밑에 작성
class Comment(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)    # 포스트 삭제 시 댓글도 모두 삭제
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 댓글 삭제 시 작성자도 모두 삭제
    content = models.TextField()                            # 댓글 내용 글자 제한 X
    created_at = models.DateTimeField(auto_now_add=True)    # 작성일
    modified_at = models.DateTimeField(auto_now=True)       # 수정일

    def __str__(self):
        return f'{self.author} : {self.content}'    # 작성자 : 댓글내용

    # admin 페이지의 [view on site] 연결
    def get_absolute_url(self):
        return f'{self.goods.get_absolute_url()}#comment-{self.pk}' # 샵(#) 뒤: 해당 id 값의 태그로 이동

    # 아바타 이미지
    def get_avatar_url(self):
        if self.author.socialaccount_set.exists(): # 여러 개의 소셜 계정으로 로그인 시
            return self.author.socialaccount_set.first().get_avatar_url() # 구글
        else: # 이메일/admin 로그인 시
            return 'https://dummyimage.com/50x50/ced4da/6c757d.jpg'

