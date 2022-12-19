# 댓글폼 Comment Form
from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta: # 클래스 안의 클래스
        model = Comment
        fields = ('content', )  # 폼에서 [댓글내용]만 사용