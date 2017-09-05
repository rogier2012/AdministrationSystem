from django.conf.urls import url, include

from gyara import views
from django.contrib.auth import views as auth_view
from django.contrib.admin import views as admin_view

app_name = 'gyara'

urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='index'),
    url(r'^transactions/add/$', views.AddTransactionView.as_view(), name='add-trans'),
    url(r'^transactions/out-view/$', views.OutView.as_view(), name='out-view'),
    url(r'^transactions/in-view/$', views.InView.as_view(), name='in-view'),
    url(r'^transactions/all-month/$', views.AllMonthView.as_view(), name='all-month'),
    url(r'^transactions/all-month/(?P<month>[0-9]+)/$', views.AllMonthView.as_view(), name='all-month'),
    url(r'^transactions/all-month/(?P<month>[0-9]+)/(?P<year>[0-9]+)/$', views.AllMonthView.as_view(), name='all-month'),
    url(r'^transactions/change-trans/(?P<pk>[0-9]+)/$', views.ChangeTransactionView.as_view(), name='change-trans'),
    url(r'^transactions/delete-trans/(?P<pk>[0-9]+)/$', views.DeleteTransactionView.as_view(), name='delete-trans'),
    url(r'^transactions/change-cat/(?P<pk>[0-9]+)/$', views.ChangeCategoryView.as_view(), name='change-cat'),
    url(r'^transactions/delete-cat/(?P<pk>[0-9]+)/$', views.DeleteCategoryView.as_view(), name='delete-cat'),
    url(r'^transactions/cat-view/$', views.CategoryView.as_view(), name='cat-view'),
    url(r'^change-bud/(?P<pk>[0-9]+)/$', views.ChangeBudgetView.as_view(), name='change-bud'),
    url(r'^delete-bud/(?P<pk>[0-9]+)/$', views.DeleteBudgetView.as_view(), name='delete-bud'),
    url(r'^bud-view/$', views.BudgetView.as_view(), name='bud-view'),
    url(r'^transactions/import/$', views.BetterImportView.as_view(), name='better-import'),
    url(r'^prediction/$', views.PredictionView.as_view(), name='prediction'),
    url(r'^login/$', auth_view.login,
        {'template_name': 'gyara/registration/login.html', 'extra_context': {'next': '/gyara/'}}, name='login'),
    url(r'^logout/$', auth_view.logout, {'template_name': 'gyara/registration/logged_out.html'}, name='logout'),
    # url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]
