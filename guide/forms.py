from django import forms

class LoginForm(forms.Form):
    empno = forms.CharField(label="코드", max_length=20)
    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")

class SearchForm(forms.Form):
    query = forms.CharField(label="질병명", max_length=100, required=False)
