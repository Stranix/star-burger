from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Prefetch, Sum, ExpressionWrapper, F
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def fetch_with_price(self):
        return self.prefetch_related(
            Prefetch(
                'products_in_order',
                queryset=OrderElement.objects.prefetch_related('product')
            )
        ).annotate(
            price=Sum(
                ExpressionWrapper(
                    F('products_in_order__price') * F('products_in_order__quantity'),
                    output_field=models.PositiveIntegerField()
                )
            )
        )

    def suitable_restaurants(self):
        restaurant_menu_items = RestaurantMenuItem.objects.select_related(
            'restaurant', 'product'
        )

        for order in self:
            order_restaurants = []

            for order_product in order.products_in_order.all():
                product_restaurants = set(
                    menu_item.restaurant for menu_item in restaurant_menu_items
                    if order_product.product == menu_item.product
                    and menu_item.availability
                )
                order_restaurants.append(product_restaurants)

            suitable_restaurants = set.intersection(*order_restaurants)
            order.suitable_restaurants = suitable_restaurants

        return self


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('NEW', 'Новый'),
        ('COLLECT', 'В сборке'),
        ('IN_DELIVERY', 'У курьера'),
        ('COMPLETED', 'Завершен'),
    )

    PAYMENT_CHOICES = (
        ('IMMEDIATE', 'Сразу'),
        ('BANK_CARD', 'Картой'),
        ('CASH', 'Наличными'),
    )

    firstname = models.CharField('Имя', max_length=100)
    lastname = models.CharField('Фамилия', max_length=100)
    phonenumber = PhoneNumberField('Номер телефона', db_index=True)
    address = models.CharField('Адрес', max_length=200)
    status = models.CharField(
        'Cтатус',
        max_length=11,
        choices=ORDER_STATUS_CHOICES,
        default='NEW',
        db_index=True,
    )

    payment_method = models.CharField(
        verbose_name='Способ оплаты',
        max_length=9,
        choices=PAYMENT_CHOICES,
        default='BANK_CARD',
        db_index=True
    )
    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.SET_NULL,
        related_name='orders',
        verbose_name='ресторан',
        help_text='ресторан выполнения заказа',
        blank=True,
        null=True,
    )
    comment = models.TextField(
        'Комментарий',
        blank=True,
    )
    created_at = models.DateTimeField(
        'дата заказа',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'дата звонка',
        null=True,
        blank=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'дата доставки',
        null=True,
        blank=True,
        db_index=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.lastname} {self.firstname}, {self.address}"


class OrderElement(models.Model):
    order = models.ForeignKey(
        'Order',
        verbose_name='Заказ',
        related_name='products_in_order',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        'Product',
        verbose_name='Товар',
        related_name='products',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(
        'Количество',
        default=1,
        validators=[MinValueValidator(1)],

    )

    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product} {self.order}'
