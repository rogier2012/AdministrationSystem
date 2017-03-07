import decimal

from django.contrib import admin

# Register your models here.
from gyara.models import Transaction, Category, Budget


class UserSaveMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user_id = request.user
        super(UserSaveMixin, self).save_model(request, obj, form, change)


class TransactionAdmin(UserSaveMixin):
    def simple_date(self, obj):
        return obj.date.strftime("%d-%m-%Y")

    def euro(self, obj):
        return '€ ' + str(obj.value)

    simple_date.short_description = "Date"
    euro.short_description = 'Euros'
    list_display = ('description', 'simple_date', 'category', 'euro')
    list_filter = ['date']
    search_fields = ['description', 'value']

    fieldsets = (
        (None, {'fields': ('description', 'category', 'value'),
                'classes': ('wide',)}),
    )


class CategoryAdmin(UserSaveMixin):
    list_display = ('name', 'user_id','flow')
    fields = ('name', 'user_id','flow')
    readonly_fields = ('user_id',)


class BudgetAdmin(UserSaveMixin):
    list_display = ('category', 'year', 'euro')
    fields = ('category', 'year', 'value')
    readonly_fields = ('user_id',)

    def euro(self, obj):
        return '€ ' + str(obj.value)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Budget, BudgetAdmin)
