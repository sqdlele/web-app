import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from app.models import Category, Product, Profile


@pytest.mark.django_db
def test_category_str():
    category = Category.objects.create(name='Книги', slug='books')
    assert str(category) == 'Книги'


@pytest.mark.django_db
def test_product_absolute_url():
    category = Category.objects.create(name='Техника', slug='tech')
    product = Product.objects.create(
        category=category,
        name='Наушники',
        slug='headphones',
        description='Хороший звук',
        price='1999.00',
    )
    assert product.get_absolute_url() == reverse('product_detail', kwargs={'slug': 'headphones'})


@pytest.mark.django_db
def test_profile_created_in_profile_view(client):
    user = User.objects.create_user(username='ivan', password='1234pass')
    client.login(username='ivan', password='1234pass')
    response = client.get(reverse('profile'))
    assert response.status_code == 200
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_catalog_filter_by_category(client):
    cat1 = Category.objects.create(name='Одежда', slug='clothes')
    cat2 = Category.objects.create(name='Еда', slug='food')
    Product.objects.create(category=cat1, name='Куртка', slug='jacket', description='Теплая', price='5000')
    Product.objects.create(category=cat2, name='Яблоки', slug='apple', description='Свежие', price='120')
    response = client.get(reverse('catalog'), {'category': 'food'})
    assert response.status_code == 200
    products = list(response.context['products'])
    assert len(products) == 1
    assert products[0].slug == 'apple'


@pytest.mark.django_db
def test_add_to_cart(client):
    category = Category.objects.create(name='Другое', slug='other')
    product = Product.objects.create(category=category, name='Товар', slug='item', description='Описание', price='10')
    response = client.post(reverse('add_to_cart', args=[product.id]))
    assert response.status_code == 302
    session = client.session
    assert session['cart'][str(product.id)] == 1


@pytest.mark.django_db
def test_home_page_available(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_saves_phone(client):
    response = client.post(
        reverse('register'),
        {
            'username': 'petr',
            'email': 'petr@example.com',
            'phone': '+79995554433',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        },
    )
    assert response.status_code == 302
    user = User.objects.get(username='petr')
    assert user.profile.phone == '+79995554433'
