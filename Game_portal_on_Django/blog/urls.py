from django.contrib import admin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path('', views.NewsList.as_view(), name='home'),
    path('news/<slug:news_slug>', views.ShowNews.as_view(), name='news'),
    path('tag_news/<slug:tag_news_slug>', views.show_tag_news, name='tag_news'),
    path('about/', views.about, name='about'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('blog/', views.ArticleList.as_view(), name='blog'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('add_article/', views.AddArticle.as_view(), name='add_article'),
    path('article/<slug:slug>', views.ShowArticle.as_view(), name='article'),
    path('category/<slug:cat_slug>', views.GameCategory.as_view(), name='category'),
    path('edit_page/<slug:slug>', views.UpdateArticle.as_view(), name='edit_page'),
    path('delete_article/<slug:slug>', views.DeleteArticle.as_view(), name='delete_article'),
    path('cancel/', views.ArticleList.as_view(), name='cancel'),
    path('article_comment/<slug:slug>', views.ArticleCommentAdd.as_view(), name='article_comment'),
    path('edit_comment/<int:id>', views.ArticleCommentEdit.as_view(), name='edit_comment'),
    path('delete_comment/<int:id>', views.ArticleCommentDelete.as_view(), name='delete_comment'),
    path('tag/<slug:tag_slug>', views.show_tag_article, name='tag'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),

    path('password-change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
         name='password_change_done'),

    path('password-reset/', PasswordResetView.as_view(
        template_name="users/password_reset_form.html",
        email_template_name="users/password_reset_email.html",
        success_url=reverse_lazy('password_reset_done')
    ),
         name='password_reset'),

    path('password-reset/done/', PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
         name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html",
             success_url=reverse_lazy("password_reset_complete")
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name='password_reset_complete'),
]
