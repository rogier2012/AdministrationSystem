from _decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=300)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, auto_created=True)
    IN = 'IN'
    OUT = 'OUT'
    FLOW_CHOICES = ((IN, "In"), (OUT, 'Out'))
    flow = models.CharField(max_length=3, choices=FLOW_CHOICES, default=OUT)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'user_id'))


class Transaction(models.Model):
    date = models.DateField(default=timezone.now)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, auto_created=True)
    IN = 'IN'
    OUT = 'OUT'
    FLOW_CHOICES = ((IN, "In"), (OUT, 'Out'))
    flow = models.CharField(max_length=3, choices=FLOW_CHOICES, default=OUT)
    description = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        get_latest_by = "date"

    def __str__(self):
        if self.date is None:
            return self.description + " €" + str(self.value)
        else:
            return self.date.strftime("%d-%m") + ": " + self.description + " €" + str(self.value)

    @classmethod
    def from_csv(cls, user, row):
        csv_date = datetime.strptime(row.get("Datum", ""), "%Y%m%d")
        user_id = user
        value = Decimal(row.get("Bedrag (EUR)", "").replace(",", "."))
        descr = row.get("Naam / Omschrijving", "")[:100]
        if row.get("Af Bij","") == "Af":
            flow = "OUT"
        elif row.get("Af Bij","") == "Bij":
            flow = "IN"
        transaction = cls(date=csv_date, user_id=user_id, value=value, description=descr, flow=flow)
        transaction.save()


class Budget(models.Model):
    year = models.IntegerField()
    category = models.ForeignKey(Category)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, auto_created=True)

    def __str__(self):
        if self.category is None:
            return  str(self.year) + ": €" + str(self.value)
        else:
            return str(self.category) + "," + str(self.year) + ": €" + str(self.value)

    class Meta:
        unique_together = (('year', 'category', 'user_id'))

class TransactionName(models.Model):
    name = models.CharField(max_length=300)
    transaction = models.ForeignKey(Transaction)