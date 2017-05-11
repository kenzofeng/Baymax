from django.contrib import admin

from .models import Svn,Project,Map,Job,Job_Test,build,Log

class SvnAdmin(admin.ModelAdmin):
    list_display=['name']

class ProjectAdmin(admin.ModelAdmin):
    list_display=['name','scm','devurl','email']

class MapAdmin(admin.ModelAdmin):
    list_display=['project','test','testurl','robot_parameter','war','use']
    list_filter=('project','use')
        
class job_test_Inline(admin.TabularInline):
    model = Job_Test
    extra = 3
class log_Inline(admin.TabularInline):
    model = Log
    extra =3

class JobTestsAdmin(admin.ModelAdmin):
    list_display=['job','robot_parameter','name','status','report']  

class JobAdmin(admin.ModelAdmin):
    list_display=['project','status','start_time','end_time','build_command','job_number','dev_revision_number']
    inlines=[job_test_Inline,log_Inline]

class buildAdmin(admin.ModelAdmin):
    list_display=['project','build_command']  

admin.site.register(Svn ,SvnAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(Map,MapAdmin)
admin.site.register(Job,JobAdmin)
admin.site.register(Job_Test,JobTestsAdmin)
admin.site.register(build,buildAdmin)
admin.site.register(Log)