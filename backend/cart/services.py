from django.db import transaction
from decimal import Decimal
from cart.models import Cart, CartItem
from product_management.models import Product


class CartService:
    SESSION_CART_KEY = 'cart'

    @staticmethod
    def validate_stock(product, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        if not product.is_active:
            raise ValueError(f"Product '{product.name}' is not available")
        
        if product.total_stock < quantity:
            raise ValueError(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.total_stock}, Requested: {quantity}"
            )
        
        return True

    @staticmethod
    def calculate_total(cart_items):
        total = Decimal('0.00')
        for item in cart_items:
            if isinstance(item, CartItem):
                total += item.item_total
            elif isinstance(item, dict):
                price = Decimal(str(item.get('price', '0.00')))
                quantity = item.get('quantity', 0)
                total += price * quantity
        return total.quantize(Decimal('0.00'))

    @staticmethod
    def get_product_price(product):
        if product.discount_price and product.discount_price > 0:
            return product.discount_price
        return product.regular_price

    @staticmethod
    def get_or_create_cart(user=None):
        if user and user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            return cart, created
        
        return None, False

    @classmethod
    def get_session_cart(cls, request):
        cart = request.session.get(cls.SESSION_CART_KEY, {})
        return cart

    @classmethod
    def save_session_cart(cls, request, cart_data):
        request.session[cls.SESSION_CART_KEY] = cart_data
        request.session.modified = True

    @classmethod
    @transaction.atomic
    def add_to_cart(cls, user, request, product_id, quantity=1):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} does not exist")

        cls.validate_stock(product, quantity)
        
        price = cls.get_product_price(product)
        item_total = price * quantity

        if user and user.is_authenticated:
            cart, _ = cls.get_or_create_cart(user)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'item_total': item_total}
            )
            
            if not created:
                new_quantity = cart_item.quantity + quantity
                cls.validate_stock(product, new_quantity)
                cart_item.quantity = new_quantity
                cart_item.item_total = price * new_quantity
                cart_item.save()
            
            cls.update_cart_totals(cart)
            return cls.get_cart_details(cart)
        else:
            session_cart = cls.get_session_cart(request)
            product_key = str(product_id)
            
            if product_key in session_cart:
                new_quantity = session_cart[product_key]['quantity'] + quantity
                cls.validate_stock(product, new_quantity)
                session_cart[product_key]['quantity'] = new_quantity
                session_cart[product_key]['item_total'] = float(price * new_quantity)
            else:
                session_cart[product_key] = {
                    'product_id': product_id,
                    'product_name': product.name,
                    'price': float(price),
                    'quantity': quantity,
                    'item_total': float(item_total)
                }
            
            cls.save_session_cart(request, session_cart)
            return cls.get_session_cart_details(session_cart)

    @classmethod
    @transaction.atomic
    def update_cart_item(cls, user, request, product_id, quantity):
        if quantity <= 0:
            return cls.remove_from_cart(user, request, product_id)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} does not exist")

        cls.validate_stock(product, quantity)
        
        price = cls.get_product_price(product)
        item_total = price * quantity

        if user and user.is_authenticated:
            cart, _ = cls.get_or_create_cart(user)
            
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                cart_item.quantity = quantity
                cart_item.item_total = item_total
                cart_item.save()
            except CartItem.DoesNotExist:
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    item_total=item_total
                )
            
            cls.update_cart_totals(cart)
            return cls.get_cart_details(cart)
        else:
            session_cart = cls.get_session_cart(request)
            product_key = str(product_id)
            
            session_cart[product_key] = {
                'product_id': product_id,
                'product_name': product.name,
                'price': float(price),
                'quantity': quantity,
                'item_total': float(item_total)
            }
            
            cls.save_session_cart(request, session_cart)
            return cls.get_session_cart_details(session_cart)

    @classmethod
    @transaction.atomic
    def remove_from_cart(cls, user, request, product_id):
        if user and user.is_authenticated:
            cart, _ = cls.get_or_create_cart(user)
            
            try:
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                cart_item.delete()
            except CartItem.DoesNotExist:
                pass
            
            cls.update_cart_totals(cart)
            return cls.get_cart_details(cart)
        else:
            session_cart = cls.get_session_cart(request)
            product_key = str(product_id)
            
            if product_key in session_cart:
                del session_cart[product_key]
                cls.save_session_cart(request, session_cart)
            
            return cls.get_session_cart_details(session_cart)

    @classmethod
    @transaction.atomic
    def clear_cart(cls, user, request):
        if user and user.is_authenticated:
            cart, _ = cls.get_or_create_cart(user)
            CartItem.objects.filter(cart=cart).delete()
            cls.update_cart_totals(cart)
            return cls.get_cart_details(cart)
        else:
            cls.save_session_cart(request, {})
            return cls.get_session_cart_details({})

    @classmethod
    def get_cart(cls, user, request):
        if user and user.is_authenticated:
            cart, _ = cls.get_or_create_cart(user)
            return cls.get_cart_details(cart)
        else:
            session_cart = cls.get_session_cart(request)
            return cls.get_session_cart_details(session_cart)

    @classmethod
    def get_cart_details(cls, cart):
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        
        items = []
        for item in cart_items:
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'price': float(cls.get_product_price(item.product)),
                'quantity': item.quantity,
                'item_total': float(item.item_total)
            })
        
        total = cls.calculate_total(cart_items)
        number_of_items = sum(item.quantity for item in cart_items)
        
        return {
            'cart_id': cart.id,
            'items': items,
            'total': float(total),
            'number_of_items': number_of_items
        }

    @classmethod
    def get_session_cart_details(cls, session_cart):
        items = []
        cart_items_list = []
        
        for product_key, item_data in session_cart.items():
            item = {
                'product_id': item_data['product_id'],
                'product_name': item_data.get('product_name', ''),
                'price': item_data['price'],
                'quantity': item_data['quantity'],
                'item_total': item_data['item_total']
            }
            items.append(item)
            cart_items_list.append(item)
        
        total = cls.calculate_total(cart_items_list)
        number_of_items = sum(item['quantity'] for item in items)
        
        return {
            'cart_id': None,
            'items': items,
            'total': float(total),
            'number_of_items': number_of_items
        }

    @staticmethod
    def update_cart_totals(cart):
        cart_items = CartItem.objects.filter(cart=cart)
        
        total = CartService.calculate_total(cart_items)
        number_of_items = sum(item.quantity for item in cart_items)
        
        cart.total = total
        cart.number_of_items = number_of_items
        cart.save()
        
        return cart

    @classmethod
    @transaction.atomic
    def merge_session_cart_to_user_cart(cls, user, request):
        if not user or not user.is_authenticated:
            return None
        
        session_cart = cls.get_session_cart(request)
        
        if not session_cart:
            cart, _ = cls.get_or_create_cart(user)
            return cls.get_cart_details(cart)
        
        cart, _ = cls.get_or_create_cart(user)
        
        for product_key, item_data in session_cart.items():
            product_id = item_data['product_id']
            quantity = item_data['quantity']
            
            try:
                product = Product.objects.get(id=product_id)
                
                try:
                    cls.validate_stock(product, quantity)
                except ValueError:
                    continue
                
                price = cls.get_product_price(product)
                
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity, 'item_total': price * quantity}
                )
                
                if not created:
                    new_quantity = cart_item.quantity + quantity
                    try:
                        cls.validate_stock(product, new_quantity)
                        cart_item.quantity = new_quantity
                        cart_item.item_total = price * new_quantity
                        cart_item.save()
                    except ValueError:
                        pass
                        
            except Product.DoesNotExist:
                continue
        
        cls.update_cart_totals(cart)
        
        cls.save_session_cart(request, {})
        
        return cls.get_cart_details(cart)
