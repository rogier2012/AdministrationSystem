import csv
import datetime
import os
from _csv import QUOTE_NONE, QUOTE_ALL

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import IntegrityError
from django.db.models import Sum
from django.forms import modelformset_factory
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from finance.settings import MEDIA_ROOT
from gyara.category_prediction import get_category_prediction
from gyara.forms import UploadFileForm, CategoryForm, TransactionForm, TransactionFormSet
from gyara.models import Transaction, Category, Budget


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url = '/gyara/login/'
    template_name = 'gyara/dashboard.html'
    permission_required = 'gyara.can_view'
    model = Transaction

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DashboardView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        context['lastest_in'] = Transaction.objects.filter(user_id=self.request.user) \
                                    .filter(flow__exact="IN").order_by('-date')[:10]
        context['lastest_out'] = Transaction.objects.filter(user_id=self.request.user) \
                                     .filter(flow__exact="OUT").order_by('-date')[:10]
        context['todolist'] = Transaction.objects.filter(category=None)

        distr = list()
        current_month = timezone.now().month
        for category in Category.objects.all().filter(user_id=self.request.user):
            ds = Transaction.objects.filter(user_id=self.request.user).filter(flow__exact="OUT") \
                .filter(date__month=2).filter(category=category).aggregate(Sum('value'))
            value = ds.get('value__sum', 0)
            print()

            distr.append({'title': category.name, 'value': value})

        context['category_distribution'] = mark_safe(str(distr))
        return context


class AddTransactionView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Transaction
    fields = ['description', 'flow', 'date', 'category', 'value']
    template_name = 'gyara/transaction_form_update.html'
    success_url = reverse_lazy('gyara:add-trans')
    permission_required = 'gyara.can_add'

    def get_context_data(self, **kwargs):
        context = super(AddTransactionView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        context['action'] = "Create"
        return context

    def form_invalid(self, form):
        response = super(AddTransactionView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        form.instance.user_id = self.request.user
        response = super(AddTransactionView, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class ChangeTransactionView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Transaction

    template_name = 'gyara/transaction_form_update.html'
    success_url = reverse_lazy('gyara:index')
    permission_required = 'gyara.can_update'
    form_class = TransactionForm

    def get_context_data(self, **kwargs):
        context = super(ChangeTransactionView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        context['action'] = "Update"
        description = Transaction.objects.get(pk=self.object.pk).description
        context['prediction'] = get_category_prediction(self.request.user, description)
        return context


class DeleteTransactionView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Transaction
    permission_required = 'gyara.can_delete'
    success_url = reverse_lazy('gyara:all-month')

    def get_context_data(self, **kwargs):
        context = super(DeleteTransactionView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        return context


class OutView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "gyara/category_overview.html"
    permission_required = 'gyara.can_view'

    def get_context_data(self, **kwargs):
        context = super(OutView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['flow'] = "Out"
        context['has_permission'] = self.has_permission()
        month = {"January": dict(), "February": dict(), "March": dict(), "April": dict(), "May": dict(), "June": dict(),
                 "July": dict(), "August": dict(), "September": dict(), "October": dict(), "November": dict(),
                 "December": dict()}

        month_total = dict()
        for current_month, category_dict in month.items():
            d = datetime.datetime.strptime(current_month, "%B")
            cats = Category.objects.all()
            actual_total = 0
            budget_total = 0
            for cat in cats:
                ds = Transaction.objects.filter(user_id=self.request.user).filter(category__flow__exact="OUT") \
                    .filter(date__month=d.month).filter(category=cat).aggregate(Sum('value'))
                s = ds.get('value__sum')
                if s is None:
                    category_dict[cat.name] = [0]
                else:
                    category_dict[cat.name] = [s]
                    actual_total += s
                try:
                    obj = Budget.objects.get(user_id=self.request.user, category=cat, year=timezone.now().year,
                                             category__flow__exact="OUT")
                    category_dict[cat.name].append(round(obj.value / 12, 2))
                    budget_total += obj.value / 12
                except ObjectDoesNotExist:
                    category_dict[cat.name].append(0)
                category_dict[cat.name].append(category_dict[cat.name][1] - category_dict[cat.name][0])
            month_total[current_month] = [actual_total]
            month_total[current_month].append(round(budget_total, 2))
            month_total[current_month].append(month_total[current_month][1] - month_total[current_month][0])
        context['months'] = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                             "October", "November", "December"]
        context['month_total'] = month_total
        context['month_information'] = month
        return context


class InView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "gyara/category_overview.html"
    permission_required = 'gyara.can_view'

    def get_context_data(self, **kwargs):
        context = super(InView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['flow'] = "In"
        context['has_permission'] = self.has_permission()
        month = {"January": dict(), "February": dict(), "March": dict(), "April": dict(), "May": dict(), "June": dict(),
                 "July": dict(), "August": dict(), "September": dict(), "October": dict(), "November": dict(),
                 "December": dict()}

        month_total = dict()
        for current_month, category_dict in month.items():
            d = datetime.datetime.strptime(current_month, "%B")
            cats = Category.objects.all()
            actual_total = 0
            budget_total = 0
            for cat in cats:
                ds = Transaction.objects.filter(user_id=self.request.user).filter(category__flow__exact="IN") \
                    .filter(date__month=d.month).filter(category=cat).aggregate(Sum('value'))
                s = ds.get('value__sum')
                if s is None:
                    category_dict[cat.name] = [0]
                else:
                    category_dict[cat.name] = [s]
                    actual_total += s
                try:
                    obj = Budget.objects.get(user_id=self.request.user, category=cat, year=timezone.now().year)
                    category_dict[cat.name].append(round(obj.value / 12, 2))
                    budget_total += obj.value / 12
                except ObjectDoesNotExist:
                    category_dict[cat.name].append(0)
                category_dict[cat.name].append(category_dict[cat.name][0] - category_dict[cat.name][1])
            month_total[current_month] = [actual_total]
            month_total[current_month].append(round(budget_total, 2))
            month_total[current_month].append(month_total[current_month][0] - month_total[current_month][1])
        context['months'] = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                             "October", "November", "December"]
        context['month_total'] = month_total
        context['month_information'] = month
        return context


class AllMonthView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "gyara/all_transactions_month.html"
    permission_required = 'gyara.can_view'

    def get(self, request, *args, **kwargs):
        if len(self.kwargs) > 0:
            if int(self.kwargs['month']) > 12:
                raise Http404("Only twelve months")

        return super(AllMonthView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllMonthView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()

        if len(self.kwargs) > 0:
            date = datetime.datetime.strptime(kwargs['month'] + str(timezone.now().year), "%m%Y")
        else:
            date = timezone.now()
        context['current_month'] = date.strftime("%B")
        context['transactions'] = Transaction.objects.filter(user_id=self.request.user).filter(
            date__year=date.year).filter(date__month=date.month).order_by("date")
        total_in = Transaction.objects.filter(user_id=self.request.user).filter(date__month=date.month).filter(
            flow__exact="IN").aggregate(Sum('value')).get("value__sum", 0)
        total_out = Transaction.objects.filter(user_id=self.request.user).filter(date__month=date.month).filter(
            flow__exact="OUT").aggregate(Sum('value')).get("value__sum", 0)
        if total_in is None:
            total_in = 0
        if total_out is None:
            total_out = 0
        context['balance'] = total_in - total_out

        return context


class CategoryView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'gyara/category_view_add.html'
    permission_required = 'gyara.can_view'
    form_class = CategoryForm
    model = Category
    # fields = ['name','flow']

    success_url = reverse_lazy('gyara:cat-view')

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        context['categories'] = Category.objects.filter(user_id=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.user_id = self.request.user
        try:
            response = super(CategoryView, self).form_valid(form)
        except IntegrityError:
            form.add_error("name", "Name already in use")
            response = super(CategoryView, self).form_invalid(form)

        return response


class ChangeCategoryView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    fields = ['name', 'flow']
    success_url = reverse_lazy('gyara:cat-view')
    permission_required = 'gyara.can_update'

    def get_context_data(self, **kwargs):
        context = super(ChangeCategoryView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        context['action'] = "Change"
        return context


class DeleteCategoryView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    permission_required = 'gyara.can_delete'
    success_url = reverse_lazy('gyara:cat-view')

    def get_context_data(self, **kwargs):
        context = super(DeleteCategoryView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        return context


class BudgetView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'gyara/budget_view.html'
    context_object_name = 'budgets'
    permission_required = ('gyara.can_view', 'gyara.can_add')
    model = Budget
    fields = ['year', 'category', 'value']
    success_url = reverse_lazy('gyara:bud-view')

    def form_valid(self, form):
        form.instance.user_id = self.request.user

        try:
            response = super(BudgetView, self).form_valid(form)
        except IntegrityError:
            form.add_error(None, error="Category,Year combination already in use")
            response = super(BudgetView, self).form_invalid(form)
        return response

    def get_context_data(self, **kwargs):
        context = super(BudgetView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        context['budgets'] = Budget.objects.filter(user_id=self.request.user).filter(year=timezone.now().year)
        return context


class ChangeBudgetView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Budget
    fields = ['category', 'year', 'value']
    success_url = reverse_lazy('gyara:bud-view')
    permission_required = 'gyara.can_update'

    def get_context_data(self, **kwargs):
        context = super(ChangeBudgetView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        context['action'] = "Change"
        return context


class DeleteBudgetView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Budget
    permission_required = 'gyara.can_delete'
    success_url = reverse_lazy('gyara:bud-view')

    def get_context_data(self, **kwargs):
        context = super(DeleteBudgetView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['has_permission'] = self.has_permission()
        return context


class ImportView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = 'gyara/import.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('gyara:import-view')
    permission_required = 'gyara.can_upload'

    def get_context_data(self, **kwargs):
        context = super(ImportView, self).get_context_data(**kwargs)
        context['has_permission'] = self.has_permission()
        return context

    def form_valid(self, form):
        uploaded_file = self.request.FILES['file']
        path = MEDIA_ROOT + "/csvu_" + uploaded_file.name
        # Write the file to disk
        fout = open(path, 'wb')
        for chunk in uploaded_file.chunks():
            fout.write(chunk)
        fout.close()

        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Transaction.from_csv(self.request.user, row)

        os.remove(path)
        return super(ImportView, self).form_valid(form)


class PredictionView(View):
    def get(self, request, *args, **kwargs):
        description = request.GET.get("description", "")
        data = dict()
        data['prediction'] = get_category_prediction(self.request.user, description)

        return JsonResponse(data)


class BetterImportView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    form_class = TransactionForm
    template_name = "gyara/import_new.html"
    success_url = reverse_lazy('gyara:better-import')
    permission_required = 'gyara.can_upload'

    def get_context_data(self, **kwargs):
        context = super(BetterImportView, self).get_context_data(**kwargs)
        context['has_permission'] = self.has_permission()
        context['categories'] = Category.objects.all()
        context['flows'] = ['IN', 'OUT']
        return context

    def formset_valid(self, formset):
        if formset.is_valid():
            for form in formset.forms:
                form.instance.user_id = self.request.user
            formset.save()
            return True
        return False
