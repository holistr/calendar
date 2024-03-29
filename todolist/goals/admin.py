from django.contrib import admin

from goals.models import GoalCategory, Board, Goal, GoalComment


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'user', 'board')


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Board)
admin.site.register(Goal)
admin.site.register(GoalComment)
