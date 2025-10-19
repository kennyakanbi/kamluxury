import uuid
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.conf import settings
from listings.models import Property
from .utils import init_transaction, verify_transaction

def pay_init(request, slug):
    prop = Property.objects.get(slug=slug)
    email = request.GET.get('email') or 'guest@example.com'
    amount_naira = float(request.GET.get('amount') or (prop.initial_deposit or prop.price))
    amount_kobo = int(amount_naira * 100)
    reference = uuid.uuid4().hex
    callback_url = request.build_absolute_uri(reverse('checkout:pay_verify'))

    data = init_transaction(email, amount_kobo, reference, callback_url)
    auth_url = data['data']['authorization_url']
    request.session['pay_ref'] = reference
    request.session['pay_slug'] = slug
    return redirect(auth_url)

def pay_verify(request):
    ref = request.GET.get('reference') or request.session.get('pay_ref')
    if not ref:
        return HttpResponseBadRequest('Missing reference')
    result = verify_transaction(ref)
    status = result['data']['status']
    slug = request.session.get('pay_slug')
    ctx = {'status': status, 'prop': Property.objects.filter(slug=slug).first()}
    return render(request, 'listings/payment_result.html', ctx)
