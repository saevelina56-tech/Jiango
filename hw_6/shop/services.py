from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, Order, OrderItem


@transaction.atomic
def create_order(cart_items, status='new'):
    product_ids = [item['product_id'] for item in cart_items]

    products = (
        Product.objects
        .select_for_update()
        .filter(id__in=product_ids)
    )
    products_map = {p.id: p for p in products}

    if len(products_map) != len(set(product_ids)):
        raise ValidationError('Некоторые товары не найдены')

    for item in cart_items:
        p = products_map[item['product_id']]
        if p.stock < item['quantity']:
            raise ValidationError(f'Недостаточно товара «{p.name}» на складе')

    order = Order.objects.create(status=status)

    order_items = []
    for item in cart_items:
        p = products_map[item['product_id']]
        p.stock -= item['quantity']
        p.save(update_fields=['stock'])

        order_items.append(OrderItem(
            order=order,
            product=p,
            quantity=item['quantity'],
            price=p.price,
        ))

    OrderItem.objects.bulk_create(order_items)
    return order