from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.mail import send_mail, BadHeaderError
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import *
from .models import *
from .utils import *

info = {}


class NewsList(ListView):
    """ Представление для просмотра списка Новостей"""
    model = NewsBlock
    template_name = 'blog/platform.html'
    context_object_name = 'page'
    paginate_by = 3
    extra_context = {'title': 'Самые свежие новости для игроков'}


class ShowNews(DetailView):
    """ Представление для просмотра новости"""
    model = NewsBlock
    template_name = 'blog/news_open.html'
    slug_url_kwarg = 'news_slug'
    context_object_name = 'page'


def show_tag_news(request, tag_news_slug):
    tag = get_object_or_404(TagNews, slug=tag_news_slug)
    news = tag.tags.filter(status=NewsBlock.Status.PUBLISHED)
    data = {
        'title': f'tag: {tag.tag}',
        'page': news,
    }
    return render(request, 'blog/platform.html', data)


class ArticleList(DataMixin, ListView):
    """ Представление для просмотра списка статей"""
    model = GamePost
    template_name = 'blog/article.html'
    context_object_name = 'page'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Все категории')
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return GamePost.objects.filter(status='published').select_related(
            'cat')  # жадная загрузка связанных данных избегаем дубли запросов


class GameCategory(DataMixin, ListView):
    """ Представление для вывода категорий статей """
    model = GamePost
    template_name = 'blog/article.html'
    context_object_name = 'page'
    allow_empty = False  # Вызывает исключение если страница не найдена

    def get_queryset(self):
        return GamePost.objects.filter(cat__slug=self.kwargs['cat_slug'], status='published').select_related(
            'cat')  # жадная загрузка связанных данных

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name),
                                      cat_selected=c.pk)
        return dict(list(context.items()) + list(c_def.items()))


class ShowArticle(DataMixin, DetailView):
    """ Представление для просмотра статьи"""
    model = GamePost
    template_name = 'blog/article_open.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = Comment.objects.filter(article_id__slug=self.kwargs['slug'], active=True).order_by('-created')
        paginator = Paginator(comment, 3)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['slug'] = self.kwargs['slug']
        c_def = self.get_user_context(title=context['page'])
        return dict(list(context.items()) + list(c_def.items()))


class ArticleCommentAdd(LoginRequiredMixin, DataMixin, CreateView):
    """ Представление для добавления Комментарий статей"""
    form_class = CommentForm
    template_name = 'blog/article_comment.html'
    context_object_name = 'page'
    login_url = '/login/'

    def get_success_url(self, **kwargs):

        if kwargs == None:
            return reverse_lazy('article', args=(self.object.slug,))
        else:
            return reverse_lazy('article', kwargs={'slug': self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавление Комментария', obj=self.kwargs['slug'])
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        form.instance.author_id = self.request.user
        form.instance.email = get_user_model().objects.get(username=self.request.user).email
        form.instance.article_id = GamePost.objects.get(slug=self.kwargs.get("slug"))
        return super().form_valid(form)


class ArticleCommentDelete(DataMixin, DeleteView):
    """ Представление для удаления Комментарий статей"""
    model = Comment
    pk_url_kwarg = 'id'
    template_name = 'blog/del_context.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Удалить комментарий')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self, **kwargs):
        return reverse_lazy('article', args=(self.object.article_id.slug,))


class ArticleCommentEdit(DataMixin, UpdateView):
    """ Представление для редактирования Комментарий статей"""
    model = Comment
    pk_url_kwarg = 'id'
    fields = ['content', 'photo', 'photo1', 'photo2', 'active']
    template_name = 'blog/edit_comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Редактирование комментария')
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self, **kwargs):
        return reverse_lazy('article', args=(self.object.article_id.slug,))


class AddArticle(LoginRequiredMixin, DataMixin, CreateView):
    """ Представление для добавления статей"""
    form_class = AddArticleForm
    template_name = 'blog/article_add.html'
    success_url = reverse_lazy('blog')
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавление статьи')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)


class UpdateArticle(DataMixin, UpdateView):
    """ Представление для редактирования статей"""
    model = GamePost
    form_class = AddArticleForm
    # fields = ['title', 'content', 'photo', 'status', 'cat']
    template_name = 'blog/article_update.html'
    success_url = reverse_lazy('blog')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Редактирование статьи')
        return dict(list(context.items()) + list(c_def.items()))


class DeleteArticle(DataMixin, DeleteView):
    """ Представление для удаления статей"""
    model = GamePost
    template_name = 'blog/del_context.html'
    success_url = reverse_lazy("blog")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Удалить статью')
        return dict(list(context.items()) + list(c_def.items()))


# def games_platform(request):
#     context = {
#         'menu': menu,
#         'title': 'Новости в мире игр'
#     }
#     return render(request, 'blog/platform.html', context=context)


def about(request):
    context = {
        'menu': menu,
        'title': 'О сайте'
    }
    return render(request, 'blog/about.html', context=context)


def logoutuser(request):
    logout(request)
    return redirect('login')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def show_tag_article(request, tag_slug):
    tag = get_object_or_404(TagArticle, slug=tag_slug)
    article = tag.tags.filter(status="published")
    data = {
        'title': f'tag: {tag.tag}',
        'page': article,
        'cat_selected': None,
    }
    return render(request, 'blog/article.html', data)


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': "Профиль пользователя"}

    def get_success_url(self):
        return reverse_lazy('blog')

    def get_object(self, queryset=None):
        ''' Метод для определения текущего пользователя'''
        return self.request.user


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "users/password_change_form.html"
