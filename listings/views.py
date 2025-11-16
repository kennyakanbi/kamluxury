import logging
from urllib.parse import quote
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils.html import format_html
from cloudinary.utils import cloudinary_url
from .models import Property, Category
from .forms import LeadForm
from django.shortcuts import get_object_or_404, render, redirect


logger = logging.getLogger(__name__)

# Optionally support UnitOption if present
try:
    from .models import UnitOption  # noqa: F401
    HAS_UNITOPTION = True
except Exception:
    HAS_UNITOPTION = False


def about(request):
    return render(request, 'listings/about.html')


# temporary debug view — remove after use
@staff_member_required
def debug_cloudinary(request):
    """
    Shows which storage/cloudinary settings the running process actually sees.
    Only accessible by logged-in staff users.
    """
    out = []
    out.append(f"DEFAULT_FILE_STORAGE={getattr(settings, 'DEFAULT_FILE_STORAGE', 'MISSING')}")
    # CLOUDINARY_URL may be set in env or settings
    out.append(f"CLOUDINARY_URL_SET={'YES' if getattr(settings, 'CLOUDINARY_URL', '') else 'NO'}")
    # read CLOUDINARY_STORAGE dict if present
    cloud_name = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', None)
    out.append(f"CLOUDINARY_STORAGE.CLOUD_NAME={cloud_name or 'MISSING'}")
    out.append(f"MEDIA_ROOT={getattr(settings, 'MEDIA_ROOT', None)}")
    out.append(f"MEDIA_URL={getattr(settings, 'MEDIA_URL', None)}")
    return HttpResponse('<br>'.join(out))


def activities(request):
    return render(request, 'listings/activities.html')


def home(request):
    static_slides = [
        {"img": "hero/slide-1.png", "title": "Palm City", "subtitle": "Luxury waterfront living", "url": "/properties/palm-city/"},
        {"img": "hero/slide-2.png", "title": "Chevy Castle", "subtitle": "Modern apartments", "url": "/properties/chevy-castle/"},
        {"img": "hero/slide-3.png", "title": "Autograph Lagos", "subtitle": "Smart living", "url": "/properties/autograph/"},
        {"img": "hero/slide-4.png", "title": "Lekki Heights", "subtitle": "Prime investment", "url": "/properties/lekki-heights/"},
    ]

    featured = Property.objects.filter(is_featured=True).order_by('-created_at')[:6]
    whatsapp_link = "https://wa.me/2348123456789?text=Hello%20Kam%20Luxury!"

    return render(request, "listings/home.html", {
        "static_slides": static_slides,
        "featured": featured,
        "whatsapp_link": whatsapp_link,
    })

def property_detail(request, slug):
    obj = get_object_or_404(Property, slug=slug)
    images_list = [img.url for img in (obj.cover, obj.gallery1, obj.gallery2) if img][:3]
    options = obj.options.all() if hasattr(obj, 'options') else []
    return render(request, "listings/property_detail.html", {
        "obj": obj,
        "images": images_list,
        "options": options,
        "whatsapp_link": "https://wa.me/2348123456789?text=I'm%20interested%20in%20this%20property"
    })

def property_list(request):
    qs = Property.objects.all().order_by('-created_at')
    q = request.GET.get('q')
    cat = request.GET.get('cat')
    minp = request.GET.get('minp')
    maxp = request.GET.get('maxp')

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(location__icontains=q) |
            Q(description__icontains=q)
        )
    if cat:
        qs = qs.filter(category=cat)

    # Price filter works with legacy Property.price or any options__price
    if minp:
        if HAS_UNITOPTION:
            qs = qs.filter(Q(price__gte=minp) | Q(options__price__gte=minp))
        else:
            qs = qs.filter(price__gte=minp)
    if maxp:
        if HAS_UNITOPTION:
            qs = qs.filter(Q(price__lte=maxp) | Q(options__price__lte=maxp))
        else:
            qs = qs.filter(price__lte=maxp)

    qs = qs.distinct()

    paginator = Paginator(qs, 9)
    page = request.GET.get('page')
    properties = paginator.get_page(page)
    return render(request, 'listings/property_list.html', {
        'properties': properties,
        'Category': Category,
        'q': q, 'cat': cat, 'minp': minp, 'maxp': maxp,
    })


def contact_agent(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.property = property
            lead.save()
            return redirect(property.get_absolute_url())
    else:
        form = LeadForm()
    return render(request, "listings/contact_agent.html", {"property": property, "form": form})
