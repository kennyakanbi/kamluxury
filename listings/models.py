# listings/models.py
from django.db import models
from django.urls import reverse

class Category(models.TextChoices):
    STUDIO = 'STUDIO', 'Studio Apartment'
    RESIDENT = 'RESIDENT', 'Residential'
    ONE_BR = '1BR', '1 Bedroom Apartment'
    TWO_BR = '2BR', '2 Bedroom Apartment'
    THREE_BR = '3BR', '3 Bedroom Apartment'
    FOUR_BR = '4BR', '3 Bedroom Apartment'
    FARM_LAND = 'FARM', 'Farm Land'
    LAND_ASSET = 'LAND', 'Land Asset'
    MALL_SHOP = 'SHOP', 'Mall Shop'

class Property(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=10, choices=Category.choices, blank=True)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Keep legacy fields nullable for backward compatibility
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    initial_deposit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    installment_plan = models.CharField(max_length=200, blank=True)

    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    parking = models.PositiveIntegerField(default=0)
    square_meters = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    cover = models.ImageField(upload_to='properties/', blank=True, null=True)
    gallery1 = models.ImageField(upload_to='properties/', blank=True, null=True)
    gallery2 = models.ImageField(upload_to='properties/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listings:detail', args=[self.slug])

class UnitOption(models.Model):
    """
    A sellable option under a Property (Studio / 1BR / 2BR / etc.) with its own pricing.
    """
    property = models.ForeignKey(Property, related_name='options', on_delete=models.CASCADE)
    unit_type = models.CharField(max_length=10, choices=Category.choices)
    label = models.CharField(max_length=120, blank=True, help_text="Optional display label, e.g. '2-Bedroom + BQ'")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    initial_deposit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    plan_0_3 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    plan_3_6 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    plan_6_12 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.property.title} – {self.get_unit_type_display()}"

class Lead(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    option = models.ForeignKey(UnitOption, on_delete=models.SET_NULL, null=True, blank=True)  # <-- optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.phone}"
