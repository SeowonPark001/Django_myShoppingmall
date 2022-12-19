from django.shortcuts import render, redirect
from .models import Goods, Category, Tag, Comment, Maker
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.shortcuts import get_object_or_404
from django.db.models import Q


# 댓글 삭제 기능
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    goods = comment.goods
    # 삭제 다시 확인
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(goods.get_absolute_url())
    else:
        PermissionDenied


# Comment Form: 댓글 수정하기
class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    # comment_form.html: UpdateView가 (모델명)_form.html을 템플릿으로 인지

    # 요청 사용자가 권한ㅇ => 댓글 수정하기 페이지 보내기(dispatch)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied  # Exception 발생



# 상품 생성 - Form
class GoodsCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Goods
    fields = ['title', 'hook_text', 'content', 'head_image', 'maker', 'category']

    # goods_form.html: CreateView가 (모델명)_form.html을 템플릿으로 인지

    def get_context_data(self, object_list=None, **kwargs):
        context = super(GoodsCreate, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Goods.objects.filter(category=None).count
        context['makers'] = Maker.objects.all()
        context['no_maker_goods_count'] = Goods.objects.filter(maker=None).count

        return context

    # 폼이 올바른지 확인 (LoginRequiredMixin)
    def form_valid(self, form):
        # 요청하는 사용자 정보
        current_user = self.request.user

        # 인증된 사용자(+슈퍼유저/스탭 (UserPassesTestMixin))인 경우
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            # 해당 사용자를 폼에 해당하는 작성자로 간주
            form.instance.author = current_user
            response = super(GoodsCreate, self).form_valid(form)
            # 태그 입력
            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()             # 문자열의 전체 앞뒤 여백 제거
                tags_str = tags_str.replace(',',';')    # [,]->[;]으로 변환 , is_created
                tag_list = tags_str.split(';')          # [;] 기준으로 문자열 분리 >> 배열
                for t in tag_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response             # super(GoodsCreate, self).form_valid(form)
        else:
            return redirect('/market/')   # 인증된 사용자가 아닌 경우 market 페이지로 이동

    # (UserPassesTestMixin)
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff  # 둘 중 하나 해당 시 true 반환



# 이미 존재하는 상품 수정
class GoodsUpdate(LoginRequiredMixin, UpdateView):
    model = Goods
    fields = ['title', 'hook_text', 'content', 'head_image', 'maker', 'category']  # 등록글 속성들, 똑같이 적기 , 'tags'
    template_name = 'market/goods_update_form.html'


    def get_context_data(self, object_list=None, **kwargs):
        context = super(GoodsUpdate, self).get_context_data()
        # 태그 입력 - 기존 태그에 입력한 새 태그 추가
        if self.object.tags.exists:
            tag_str_list = list()
            for t in self.object.tags.all():
                tag_str_list.append(t.name)
            context['tags_str_default'] = ';'.join(tag_str_list)
        context['categories'] = Category.objects.all()
        context['no_category_goods_count'] = Goods.objects.filter(category=None).count
        context['makers'] = Maker.objects.all()
        context['no_maker_goods_count'] = Goods.objects.filter(category=None).count
        return context

    # 요청 사용자가 권한ㅇ => 포스트 수정하기 페이지 보내기(dispatch)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(GoodsUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied  # Exception 발생

    def form_valid(self, form):
        response = super(GoodsUpdate, self).form_valid(form)
        self.object.tags.clear()    # 기존 태그들을 삭제 후 새 태그들 등록
        # 태그 입력
        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()             # 문자열의 전체 앞뒤 여백 제거
            tags_str = tags_str.replace(',', ';')   # [,]->[;]으로 변환 , is_created
            tag_list = tags_str.split(';')          # [;] 기준으로 문자열 분리 >> 배열
            for t in tag_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        return response



# CBV: ListView 사용 >> 상품 목록 페이지 만들기
class GoodsList(ListView):
    model = Goods
    # goods_list.html: ListView이 (모델명)_list.html을 템플릿으로 인지

    ordering = '-pk'    # 최신등록순
    paginate_by = 5     # 18장 Pagination: 한 페이지에 포스트 n개씩만 보여주기

    # Context 데이터 전달
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GoodsList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_goods_count'] = Goods.objects.filter(category=None).count
        context['makers'] = Maker.objects.all()
        context['no_maker_goods_count'] = Goods.objects.filter(category=None).count
        return context


# 상품 상세 페이지
class GoodsDetail(DetailView):
    model = Goods
    # goods_detail.html: ListView이 (모델명)_detail.html을 템플릿으로 인지

    # 카테고리 context 데이터 전달
    def get_context_data(self, **kwargs):
        context = super(GoodsDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_goods_count'] = Goods.objects.filter(category=None).count
        context['makers'] = Maker.objects.all()
        context['no_maker_goods_count'] = Goods.objects.filter(category=None).count
        context['comment_form'] = CommentForm   # 추가
        return context


# 검색 기능 - GoodsList 밑에 작성
class GoodsSearch(GoodsList): # ListView 상속, goods_list.html
    paginate_by = None

    # 검색어 -> set
    def get_queryset(self):
        q = self.kwargs['q']    # 'q'라는 인자를 받아와서 가져옴
        goods_list = Goods.objects.filter(    # Q: 여러 조건 사용
            Q(title__contains=q) | Q(tags__name__contains=q) # = tags.name.contains(파이썬 문법)
        ).distinct()    # 중복으로 검색되는 요소가 있을 경우, 하나만 남김
        return goods_list

    # Context 데이터 전달
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GoodsSearch, self).get_context_data()
        q = self.kwargs['q']
        context['search_info'] = f'Search: {q} ({self.get_queryset().count()})'
        return context


# 카테고리 & 제조사 & 태그 & 댓글: GoodsDetail 안x 밖ㅇ (카테고리, 태그 => GoodsList에서도 사용ㅇ)

# CommentForm: 새 댓글 작성하기
def new_comment(request, pk):
    # 로그인한 유저인 경우
    if request.user.is_authenticated:
        goods = get_object_or_404(Goods,pk=pk)

        # 요청 형식이 POST인 경우
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.goods = goods
                comment.author = request.user
                comment.save() # 서버 model에 save
                return redirect(comment.get_absolute_url()) # 해당 url로 이동
        # 요청 형식이 POST가 아닌 경우 : GET
        else:
            return redirect(goods.get_absolute_url()) # 포스트 상세 페이지로 이동
    # 로그인 X 사용자인 경우
    else:
        raise PermissionDenied


# 다대일: Category 페이지
def category_page(request, slug):  # <- slug: 매개변수로 갖고옴
    if slug == 'no_category':
        category = '미분류'
        goods_list = Goods.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        goods_list = Goods.objects.filter(category=category)

    return render(request, 'market/goods_list.html', {
        'category': category,
        'goods_list': goods_list,  # 미분류 때문에 미리 변수에 할당 / Goods.objects.filter(category=category)
        'categories': Category.objects.all(),
        'no_category_goods_count': Goods.objects.filter(category=None).count,
        'makers': Maker.objects.all(),
        'no_maker_goods_count': Goods.objects.filter(maker=None).count
    })


# 다대일: Maker 페이지
def maker_page(request, slug):  # <- slug: 매개변수로 갖고옴
    if slug == 'no_maker':
        maker = '미분류'
        goods_list = Goods.objects.filter(maker=None)
    else:
        maker = Maker.objects.get(slug=slug)
        goods_list = Goods.objects.filter(maker=maker)

    return render(request, 'market/goods_list.html', {
        # side bar의 categorym, maker
        'categories': Category.objects.all(),
        'no_category_goods_count': Goods.objects.filter(category=None).count,

        'maker': maker,
        'goods_list': goods_list,  # 미분류 때문에 미리 변수에 할당 / Goods.objects.filter(category=category)
        'makers': Maker.objects.all(),
        'no_maker_goods_count': Goods.objects.filter(maker=None).count
    })


# 다대다 : Tag 페이지
def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    goods_list = tag.goods_set.all()

    return render(request, 'market/goods_list.html', {
        'tag': tag,
        'goods_list': goods_list,  # 미분류 때문에 미리 변수에 할당 / Goods.objects.filter(category=category)
        # side bar의 categorym, maker
        'categories': Category.objects.all(),
        'no_category_goods_count': Goods.objects.filter(category=None).count,
        'makers': Maker.objects.all(),
        'no_maker_goods_count': Goods.objects.filter(maker=None).count
    })
