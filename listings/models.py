from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField

class Category(models.TextChoices):
    STUDIO = 'STUDIO', 'Studio Apartment'
    DIPLEX = 'DUPLEX', 'Duplex'
    RESIDENT = 'RESIDENT', 'Residential'
    ONE_BR = '1BR', '1 Bedroom Apartment'
    TWO_BR = '2BR', '2 Bedroom Apartment'
    THREE_BR = '3BR', '3 Bedroom Apartment'
    FOUR_BR = '4BR', '4 Bedroom Apartment'
    FIVE_BR = '5BR', '5 Bedroom Apartment'
    FARM_LAND = 'FARM', 'Farm Land'
    LAND_ASSET = 'LAND', 'Land Asset'
    MALL_SHOP = 'SHOP', 'Mall Shop'

class Property(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=10, choices=Category.choices, blank=True)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    initial_deposit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    installment_plan = models.CharField(max_length=200, blank=True)
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    parking = models.PositiveIntegerField(default=0)
    square_meters = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    # Cloudinary fields — allow blank/null so admin won't fail when empty
    cover = CloudinaryField('cover', blank=True, null=True)
    gallery1 = CloudinaryField('gallery1', blank=True, null=True)
    gallery2 = CloudinaryField('gallery2', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("listings:detail", args=[self.slug])


class UnitOption(models.Model):
    property = models.ForeignKey(Property, related_name='options', on_delete=models.CASCADE)
    unit_type = models.CharField(max_length=10, choices=Category.choices)
    label = models.CharField(max_length=120, blank=True, help_text="Optional display label, e.g. '2-Bedroom + BQ'")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    initial_deposit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    plan_0_3 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    plan_3_6 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    plan_6_12 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.property.title} – {self.get_unit_type_display()}"


class Lead(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    option = models.ForeignKey(UnitOption, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.phone}"
