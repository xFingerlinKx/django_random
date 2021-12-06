from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from test_api.models import Token
from django.contrib.auth.models import User


class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created', 'is_active')
    search_fields = ('user__email', 'user__username')
    ordering = ('-created',)
    list_filter = ('is_active',)


class TokenInline(admin.TabularInline):
    model = Token

    def get_queryset(self, request):
        """ Only active tokens """
        queryset = Token.objects.filter(is_active=True)
        return queryset


class UserAdmin(UserAdmin):
    inlines = (TokenInline,)


admin.site.register(Token, TokenAdmin)
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
