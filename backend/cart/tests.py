from decimal import Decimal
from django.test import TestCase
from unittest.mock import Mock, patch
from cart.services import CartService
from cart.models import CartItem


class MockProduct:
    def __init__(self, id=1, name="Test Product", total_stock=10, is_active=True, 
                 regular_price=Decimal('100.00'), discount_price=None):
        self.id = id
        self.name = name
        self.total_stock = total_stock
        self.is_active = is_active
        self.regular_price = regular_price
        self.discount_price = discount_price


class CartServiceValidateStockTest(TestCase):
    
    def test_validate_stock_normal_flow(self):
        product = MockProduct(total_stock=10, is_active=True)
        quantity = 5
        
        result = CartService.validate_stock(product, quantity)
        
        self.assertTrue(result)
    
    def test_validate_stock_boundary_condition_exact_stock(self):
        product = MockProduct(total_stock=5, is_active=True)
        quantity = 5
        
        result = CartService.validate_stock(product, quantity)
        
        self.assertTrue(result)
    
    def test_validate_stock_exception_insufficient_stock(self):
        product = MockProduct(name="Test Product", total_stock=3, is_active=True)
        quantity = 5
        
        with self.assertRaises(ValueError) as context:
            CartService.validate_stock(product, quantity)
        
        self.assertIn("Insufficient stock", str(context.exception))
        self.assertIn("Test Product", str(context.exception))
        self.assertIn("Available: 3", str(context.exception))
        self.assertIn("Requested: 5", str(context.exception))
    
    def test_validate_stock_exception_inactive_product(self):
        product = MockProduct(name="Inactive Product", total_stock=10, is_active=False)
        quantity = 1
        
        with self.assertRaises(ValueError) as context:
            CartService.validate_stock(product, quantity)
        
        self.assertIn("is not available", str(context.exception))
        self.assertIn("Inactive Product", str(context.exception))
    
    def test_validate_stock_exception_zero_quantity(self):
        product = MockProduct(total_stock=10, is_active=True)
        quantity = 0
        
        with self.assertRaises(ValueError) as context:
            CartService.validate_stock(product, quantity)
        
        self.assertIn("Quantity must be greater than 0", str(context.exception))
    
    def test_validate_stock_exception_negative_quantity(self):
        product = MockProduct(total_stock=10, is_active=True)
        quantity = -1
        
        with self.assertRaises(ValueError) as context:
            CartService.validate_stock(product, quantity)
        
        self.assertIn("Quantity must be greater than 0", str(context.exception))


class CartServiceCalculateTotalTest(TestCase):
    
    def test_calculate_total_normal_flow_multiple_items(self):
        mock_item1 = Mock(spec=CartItem)
        mock_item1.item_total = Decimal('50.00')
        
        mock_item2 = Mock(spec=CartItem)
        mock_item2.item_total = Decimal('30.50')
        
        mock_item3 = Mock(spec=CartItem)
        mock_item3.item_total = Decimal('19.99')
        
        cart_items = [mock_item1, mock_item2, mock_item3]
        
        total = CartService.calculate_total(cart_items)
        
        expected = Decimal('100.49')
        self.assertEqual(total, expected)
    
    def test_calculate_total_boundary_condition_empty_cart(self):
        cart_items = []
        
        total = CartService.calculate_total(cart_items)
        
        expected = Decimal('0.00')
        self.assertEqual(total, expected)
    
    def test_calculate_total_boundary_condition_single_item(self):
        mock_item = Mock(spec=CartItem)
        mock_item.item_total = Decimal('99.99')
        
        cart_items = [mock_item]
        
        total = CartService.calculate_total(cart_items)
        
        expected = Decimal('99.99')
        self.assertEqual(total, expected)
    
    def test_calculate_total_with_dict_items(self):
        cart_items = [
            {'price': '25.50', 'quantity': 2},
            {'price': '10.00', 'quantity': 3},
        ]
        
        total = CartService.calculate_total(cart_items)
        
        expected = Decimal('81.00')
        self.assertEqual(total, expected)
    
    def test_calculate_total_mixed_items(self):
        mock_item = Mock(spec=CartItem)
        mock_item.item_total = Decimal('50.00')
        
        cart_items = [
            mock_item,
            {'price': '25.00', 'quantity': 2},
        ]
        
        total = CartService.calculate_total(cart_items)
        
        expected = Decimal('100.00')
        self.assertEqual(total, expected)
    
    def test_calculate_total_decimal_precision(self):
        mock_item1 = Mock(spec=CartItem)
        mock_item1.item_total = Decimal('0.1')
        
        mock_item2 = Mock(spec=CartItem)
        mock_item2.item_total = Decimal('0.2')
        
        cart_items = [mock_item1, mock_item2]
        
        total = CartService.calculate_total(cart_items)
        
        expected = Decimal('0.30')
        self.assertEqual(total, expected)


class CartServiceGetProductPriceTest(TestCase):
    
    def test_get_product_price_with_discount(self):
        product = MockProduct(
            regular_price=Decimal('100.00'),
            discount_price=Decimal('80.00')
        )
        
        price = CartService.get_product_price(product)
        
        self.assertEqual(price, Decimal('80.00'))
    
    def test_get_product_price_without_discount(self):
        product = MockProduct(
            regular_price=Decimal('100.00'),
            discount_price=None
        )
        
        price = CartService.get_product_price(product)
        
        self.assertEqual(price, Decimal('100.00'))
    
    def test_get_product_price_with_zero_discount(self):
        product = MockProduct(
            regular_price=Decimal('100.00'),
            discount_price=Decimal('0.00')
        )
        
        price = CartService.get_product_price(product)
        
        self.assertEqual(price, Decimal('100.00'))
