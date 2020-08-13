from django import forms
from app.models import Question, User, Answer


class SignupForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    repeatPassword = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.strip() == '':
            raise forms.ValidationError('Invalid Login')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email.strip() == '':
            raise forms.ValidationError('Invalid email')
        if ' ' in email:
            raise forms.ValidationError('Space in email')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password.strip() == '':
            raise forms.ValidationError('Invalid Password')
        if ' ' in password:
            raise forms.ValidationError('Space in Password')
        return password

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        data = super().clean()
        password = data.get('password')
        repeatPassword = data.get('repeatPassword')

        if password != repeatPassword:
            raise forms.ValidationError('Not same password')

    def save(self, commit=True):
        user = User(username=self.cleaned_data.get('username'),
                    email=self.cleaned_data.get('email'),
                    password=self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.strip() == '':
            raise forms.ValidationError('Invalid Login')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password.strip() == '':
            raise forms.ValidationError('Invalid Password')
        if ' ' in password:
            raise forms.ValidationError('Space in Password')
        return password


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'definition', 'tags']

    def __init__(self, author, *args, **kwargs):
        self.author = author
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        question = Question(title=self.cleaned_data.get('title'),
                            definition=self.cleaned_data.get('definition'),)
        question.author = self.author
        if commit:
            question.save()
        question.tags.set(self.cleaned_data.get('tags'))
        if commit:
            question.save()
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']

    def __index__(self, author, question, *args, **kwargs):
        self.author = author
        self.question = question
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = Answer(text=self.cleaned_data.get('text'))
        answer.author = self.author
        answer.question = self.question
        if commit:
            answer.save()
        return answer


class ProfileSettingsForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    image = forms.ImageField(required=False, widget=forms.FileInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.strip() == '':
            raise forms.ValidationError('Invalid Login')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email.strip() == '':
            raise forms.ValidationError('Invalid email')
        if ' ' in email:
            raise forms.ValidationError('Space in email')
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']