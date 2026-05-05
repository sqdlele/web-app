from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from app.models import Category, Event, Product, Profile


class Command(BaseCommand):
    help = "Fill database with demo shop data"

    def handle(self, *args, **options):
        demo_data = {
            "Электроника": [
                ("Беспроводные наушники", "Легкие наушники для музыки и звонков.", "3490.00"),
                ("Умная лампа", "Лампа с регулировкой яркости и теплоты света.", "1290.00"),
                ("Портативная колонка", "Компактная колонка с хорошим басом.", "2790.00"),
            ],
            "Дом": [
                ("Набор полотенец", "Мягкие хлопковые полотенца для дома.", "990.00"),
                ("Кофейная кружка", "Керамическая кружка на каждый день.", "450.00"),
                ("Плед", "Теплый плед для дивана или спальни.", "1850.00"),
            ],
            "Спорт": [
                ("Фитнес-резинка", "Эспандер для домашних тренировок.", "390.00"),
                ("Бутылка для воды", "Прочная бутылка 750 мл.", "620.00"),
                ("Коврик для йоги", "Удобный коврик для фитнеса и растяжки.", "1590.00"),
            ],
        }

        created_categories = 0
        created_products = 0

        for category_name, products in demo_data.items():
            category, category_created = Category.objects.get_or_create(
                slug=slugify(category_name, allow_unicode=True),
                defaults={"name": category_name},
            )
            if category_created:
                created_categories += 1

            for product_name, description, price in products:
                _, product_created = Product.objects.get_or_create(
                    slug=slugify(product_name, allow_unicode=True),
                    defaults={
                        "category": category,
                        "name": product_name,
                        "description": description,
                        "price": price,
                    },
                )
                if product_created:
                    created_products += 1

        user, user_created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@example.com"},
        )
        if user_created:
            user.set_password("demo12345")
            user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        if not profile.phone:
            profile.phone = "+7 900 000-00-00"
            profile.save()

        events_data = [
            ("Сезонные скидки", "Большая распродажа популярных товаров."),
            ("Новая коллекция", "Добавили свежие позиции в каталог."),
            ("Бесплатная доставка", "Акция на доставку при заказе от 3000 ₽."),
        ]
        created_events = 0
        for title, description in events_data:
            _, was_created = Event.objects.get_or_create(
                title=title,
                defaults={"description": description, "is_active": True},
            )
            created_events += int(was_created)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(f"Categories created: {created_categories}")
        self.stdout.write(f"Products created: {created_products}")
        self.stdout.write(f"Events created: {created_events}")
        self.stdout.write("Demo user: demo / demo12345")
