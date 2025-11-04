# listings/views.py
from asyncio.log import logger
from urllib.parse import quote
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Property, Category
from .forms import LeadForm
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

# Optionally support UnitOption if present
try:
    from .models import UnitOption
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
    # featured queryset used by the template
    featured = Property.objects.filter(is_featured=True)[:6]

    # Static hero slides that your template expects (paths are relative to STATIC files)
    # Update filenames if your repo uses different names or locations.
    static_slides = [
        {"img": "img/brand.png", "title": "Building Dreams, Defining Luxury"},
        {"img": "img/interior.jpeg", "title": "From Lagos to the World"},
        {"img": "img/brand_1.png", "title": "Own Your Next Address"},
    ]

    # Optional "services" used by the services loop in the template
    services = [
        {"icon": "🏡", "title": "Real Estate Sales", "desc": "Luxury homes, apartments & investment properties with flexible payment plans."},
        {"icon": "📣", "title": "Property Marketing", "desc": "Pro photos & videos, brochures, and social campaigns to showcase listings."},
        {"icon": "🧭", "title": "Consulting & Support", "desc": "Buyer guidance, investment advisory, and end-to-end client support."},
        {"icon": "⚡", "title": "Media & Branding", "desc": "Creative design, brand strategy, and content to elevate your presence."},
        {"icon": "💼", "title": "Investment Plans", "desc": "Structured opportunities and partnerships tailored to your goals."},
    ]

    # Debug logging (keeps the logging you added)
    try:
        preview = list(featured)[:3]
    except Exception:
        preview = repr(featured)
    logger.debug("DEBUG home(): featured type=%s preview=%r", type(featured), preview)

    # Render with both featured and the template-required variables
    return render(request, 'listings/home.html', {
        "featured": featured,
        "static_slides": static_slides,
        "services": services,
    })



def property_list(request):
    qs = Property.objects.all().order_by('-created_at')
    q    = request.GET.get('q')
    cat  = request.GET.get('cat')
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


# listings/views.py (property_detail)
def property_detail(request, slug):
    obj = get_object_or_404(Property.objects.prefetch_related('options'), slug=slug)

    # Get options in a predictable order (by price; change to -created if you prefer)
    options = list(getattr(obj, 'options').all().order_by('price'))

    selected_option = None
    if HAS_UNITOPTION:
        selected_option_id = request.POST.get('option_id') or request.GET.get('option_id')
        if selected_option_id:
            from .models import UnitOption  # safe import
            try:
                selected_option = UnitOption.objects.get(id=selected_option_id, property=obj)
            except UnitOption.DoesNotExist:
                selected_option = None
        elif options:
            selected_option = options[0]  # preselect first

    form = LeadForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        lead = form.save(commit=False)
        lead.property = obj
        if HAS_UNITOPTION and selected_option:
            lead.option = selected_option
        lead.save()
        return redirect(obj.get_absolute_url())

    from urllib.parse import quote
    whatsapp_number = getattr(settings, 'WHATSAPP_NUMBER', '2347036067548')
    wa_text = f"I'm interested in {obj.title}"
    if selected_option:
        wa_text += f" – {selected_option.get_unit_type_display()}"
    wa_text += f" ({request.build_absolute_uri(obj.get_absolute_url())})"
    whatsapp_link = f"https://wa.me/{whatsapp_number}?text={quote(wa_text)}"

    return render(request, 'listings/property_detail.html', {
        'obj': obj,
        'form': form,
        'whatsapp_link': whatsapp_link,
        'selected_option': selected_option,
        'options': options,               # <-- pass explicitly
    })

