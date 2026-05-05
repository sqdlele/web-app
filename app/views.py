from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ProfileUpdateForm, RegisterForm
from .models import Category, Event, Product, Profile, Purchase


def _profile(user):
    return Profile.objects.get_or_create(user=user)[0]


def _auth_redirect(request):
    return redirect('profile') if request.user.is_authenticated else None


def _cart_data(cart):
    items, total = [], Decimal('0.00')
    for p in Product.objects.filter(id__in=[int(i) for i in cart.keys()]):
        qty = cart.get(str(p.id), 0)
        line = p.price * qty
        total += line
        items.append({'product': p, 'qty': qty, 'line_total': line})
    return items, total


def _create_purchases(user, cart):
    for i, qty in cart.items():
        p = Product.objects.filter(id=int(i)).first()
        if p:
            Purchase.objects.create(user=user, product=p, quantity=qty)


def home(request):
    products = Product.objects.prefetch_related('images').order_by('?')[:3]
    events = Event.objects.filter(is_active=True)[:5]
    return render(request, 'app/home.html', {'random_products': products, 'events': events})

def about(request):
    return render(request, 'app/about.html')

def catalog(request):
    products = Product.objects.select_related('category').prefetch_related('images')
    categories = Category.objects.all()
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('category', '').strip()

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if cat:
        products = products.filter(category__slug=cat)

    return render(request, 'app/catalog.html', {
        'products': products,
        'categories': categories,
        'active_category': cat,
        'query': q,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('images'), slug=slug)
    image_id = request.GET.get('image')
    image = product.images.filter(id=image_id).first() if image_id else None
    return render(
        request,
        'app/product_detail.html',
        {'product': product, 'selected_image': image or product.images.first()},
    )

def _get_cart(request):
    return request.session.setdefault('cart', {})

@require_POST
def add_to_cart(request, product_id):
    p = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    key = str(p.id)
    cart[key] = cart.get(key, 0) + 1
    request.session.modified = True
    messages.success(request, f'Товар "{p.name}" добавлен в корзину.')
    return redirect('cart')

def cart_view(request):
    rows, total = _cart_data(_get_cart(request))
    return render(request, 'app/cart.html', {'rows': rows, 'total': total})

@require_POST
def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    return redirect('cart')

@login_required
@require_POST
def buy_now(request, product_id):
    p = get_object_or_404(Product, id=product_id)
    Purchase.objects.create(user=request.user, product=p, quantity=1)
    messages.success(request, f'Покупка "{p.name}" оформлена.')
    return redirect('profile')

@login_required
@require_POST
def checkout(request):
    cart = _get_cart(request)
    _create_purchases(request.user, cart)
    request.session['cart'] = {}
    messages.success(request, 'Покупка завершена.')
    return redirect('profile')

@login_required
def profile(request):
    profile_obj = _profile(request.user)
    purchases = Purchase.objects.select_related('product').filter(user=request.user)
    return render(request, 'app/profile.html', {'profile_obj': profile_obj, 'purchases': purchases})

@login_required
def profile_edit(request):
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=_profile(request.user))
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Данные профиля обновлены.')
        return redirect('profile')
    return render(request, 'app/profile_edit.html', {'form': form})

def register_view(request):
    if to_profile := _auth_redirect(request):
        return to_profile
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        u = form.save()
        p = _profile(u)
        p.phone = form.cleaned_data['phone']
        p.save()
        login(request, u)
        return redirect('profile')
    return render(request, 'app/auth_form.html', {'form': form, 'title': 'Регистрация'})

def login_view(request):
    if to_profile := _auth_redirect(request):
        return to_profile
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('profile')
    return render(request, 'app/auth_form.html', {'form': form, 'title': 'Вход'})

def logout_view(request):
    logout(request)
    return redirect('home')
