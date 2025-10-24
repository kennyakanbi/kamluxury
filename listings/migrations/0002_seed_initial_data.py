# listings/migrations/0002_seed_initial_data.py
from django.db import migrations
from decimal import Decimal

def create_initial_properties(apps, schema_editor):
    Property = apps.get_model("listings", "Property")
    UnitOption = apps.get_model("listings", "UnitOption")

    # Make creations idempotent using slug
    p, created = Property.objects.get_or_create(
        slug="elegant-two-bedroom-victoria",
        defaults={
            "title": "Elegant Two-Bedroom, Victoria Island",
            "location": "Victoria Island, Lagos",
            "price": Decimal("150000000.00"),
            "category": "2BR",
            "description": "A modern two-bedroom townhouse in the heart of VI.",
            "is_featured": True,
        },
    )
    UnitOption.objects.get_or_create(
        property=p,
        unit_type="2BR",
        defaults={
            "label": "2 Bedroom",
            "price": Decimal("150000000.00"),
            "initial_deposit": Decimal("15000000.00"),
        },
    )

    # Add more properties the same way (duplicate blocks)
    Property.objects.get_or_create(
        slug="premium-studio-ikeja",
        defaults={
            "title": "Premium Studio, Ikeja",
            "location": "Ikeja, Lagos",
            "price": Decimal("30000000.00"),
            "category": "STUDIO",
            "description": "Compact studio near shops and transport.",
            "is_featured": True,
        },
    )

def reverse_func(apps, schema_editor):
    Property = apps.get_model("listings", "Property")
    slugs = ["elegant-two-bedroom-victoria", "premium-studio-ikeja"]
    Property.objects.filter(slug__in=slugs).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("listings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_properties, reverse_func),
    ]
