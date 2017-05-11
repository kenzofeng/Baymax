from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from regression import views

urlpatterns = [
                url(r'(?P<project>.*)/start$',views.job_create),
                url(r'^$',views.testproject),
                url(r'^testproject/$',views.testproject,name='testproject'),
                url(r'^testproject/getall$',views.testproject_getall),
                url(r'^testproject/getproject',views.testproject_testproject),
                url(r'^testproject/add',views.testproject_add),
                url(r'^testproject/update',views.testproject_update),
                url(r'^testproject/delete',views.testproject_delete),
                url(r'^scm/getall$',views.scm_testproject),
#                 url(r'^jobstart/(?P<jobid>\d+)/$',views.job_start),
                url(r'^log/(?P<jobid>\d+)/$',views.job_log),
                url(r'^exlog/(?P<jobid>\d+)/$',views.job_log_ex),
                url(r'^report/(?P<logid>\d+)/$',views.test_log),
                url(r'^report/(?P<logid>\d+)/log.html$',views.test_log),
                url(r'^report/(?P<logid>\d+)/report.html$',views.test_report),
                url(r'^report/(?P<logid>\d+)/(?P<cid>\d+\.\d+\.html)$',views.test_compare),
                url(r'^report/(?P<logid>\d+)/deps/(?P<redfile>.+)$',views.test_redfile),
               ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)