from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.models import Category, Product, Order, OrderItem, Address, Cart, CartItem
import razorpay
from django.conf import settings
from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
# from datetime import datetime

# Create your views here.

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    



###### Categories ##########
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image')

class CategoryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

###### Endof Categories ##########



###### Products ##########
class ProductsPaginator(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'category', 'seller', 'price', 'image')

class ProductsView(ListAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    pagination_class = ProductsPaginator

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(response.data) 


class CategoryProductsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get(self, request, category_slug):
        products = Product.objects.filter(category__slug=category_slug)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get(self, request, category_slug, product_slug):
        product = Product.objects.get(slug=product_slug, category__slug=category_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

###### End of Products ##########



######### Register ##########
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return user

class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]  # Anyone can create an account
        return [IsAuthenticated()] 

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


########### End of Register ##########


####### Add to cart #########

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist")
        return value
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddToCartSerializer

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not Cart.objects.filter(user=request.user).exists():
            cart = Cart.objects.create(user=request.user)
        else:
            cart = Cart.objects.get(user=request.user)

        if CartItem.objects.filter(cart=cart, product_id=serializer.validated_data['product_id']).exists():
            cart_item = CartItem.objects.get(cart=cart, product_id=serializer.validated_data['product_id'])
            cart_item.quantity += serializer.validated_data['quantity']
            cart_item.save()
        else:
            product = Product.objects.get(id=serializer.validated_data['product_id'])
            cart_item = CartItem.objects.create(cart=cart, product_id=serializer.validated_data['product_id'], quantity=serializer.validated_data['quantity'], total= product.price * serializer.validated_data['quantity'] )
            cart_item.save()

        return Response(serializer.data)


######## End of add to cart #########



####### Remove from cart #########

class RemoveFromCartSerializer(serializers.Serializer):
    cartitem_id = serializers.IntegerField()

    def validate_cartitem_id(self, value):
        if not CartItem.objects.filter(id=value).exists():
            raise serializers.ValidationError("Cart item does not exist")
        return value
    
class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RemoveFromCartSerializer

    def post(self, request):
        serializer = RemoveFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, id=serializer.validated_data['cartitem_id'])
        cart_item.delete()

        return Response(serializer.data)
    
##### End of remove from cart ######


####### Cart #########

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.FloatField(source='product.price', read_only=True)  # Assuming Product model has a price field.

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(source='cartitem_set', many=True)

    class Meta:
        model = Cart
        fields = ['cart_items']


class CartView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

####### End of Cart ######


######## Orders ###########

class OrderItemsSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    seller = serializers.CharField(source='product.seller.username', read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemsSerializer(source='orderitem_set', many=True)
    class Meta:
        model = Order
        fields = '__all__'

class OrdersView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



######## End of Orders ########



###### Checkout ##########

class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_mode = serializers.CharField()

    def validate_address_id(self, value):
        if not Address.objects.filter(id=value).exists():
            raise serializers.ValidationError("Address does not exist")
        return value

    def validate_payment_mode(self, value):
        if value not in ['Online Payment', 'Cash on Delivery']:
            raise serializers.ValidationError("Invalid payment mode")
        return value
    

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def post(self, request):
        try:
            # Step 1: Validate input data
            serializer = CheckoutSerializer(data=request.data)

            if serializer.is_valid():
                data = serializer.validated_data
                user = request.user  # Assuming the user is authenticated
                address = Address.objects.get(id=data.get('address_id'))

                if not address:
                    return Response({"error": "Select the address"}, status=status.HTTP_404_NOT_FOUND)
                
                cart = Cart.objects.get(user=user)

                if not cart:
                    return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

                cart_items = CartItem.objects.filter(cart=cart)

                if not cart_items:
                    return Response({"error": "Cart is empty"}, status=status.HTTP_404_NOT_FOUND)

                grand_total = 0
                
                for cart_item in cart_items:
                    product = cart_item.product
                    quantity = cart_item.quantity
                    
                    grand_total += product.price * quantity
                    
                # now = datetime.now()
                # Step 2: Create a new order in the Django Order model
                order = Order.objects.create(
                    user=user,
                    total=grand_total,
                    status='Pending',  # Initial status
                    amount_due = grand_total,
                    amount_paid = 0,
                    address = address,
                    payment_mode = data['payment_mode'],
                    # receipt_number = f"REC-{now.strftime('%Y%m%d%H%M%S%f')}"
                )

                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        total=cart_item.total
                    ) for cart_item in cart_items
                ])

                CartItem.objects.filter(cart=cart).delete()

                if data['payment_mode'] == 'Online Payment': 

                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
                    # Step 3: Create an order in Razorpay
                    razorpay_order = client.order.create({
                        "amount": int(order.total * 100),  # Amount in paise (1 INR = 100 paise)
                        "currency": 'INR',
                        "receipt": f"order_rcptid_{order.id}",
                        "payment_capture": 1  # Auto-capture the payment
                    })

                    # Step 4: Save the Razorpay order_id in the Order model
                    order.razorpay_order_id = razorpay_order['id']
                    order.save()

                    # Step 5: Return the Razorpay order details to the client
                    response_data = {
                        "razorpay_order_id": order.razorpay_order_id,
                        "amount": razorpay_order['amount'],
                        "currency": razorpay_order['currency'],
                        "receipt": razorpay_order['receipt'],
                        "order_status": order.status,
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else: 
                    return Response({"message": "COD Order created successfully"}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


####### End of Checkout ######



######### Verify Payment ##########

class VerifyPaymentSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyPaymentSerializer

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.get(razorpay_order_id=serializer.validated_data['razorpay_order_id'])
        order.razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        order.razorpay_signature = serializer.validated_data['razorpay_signature']

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
        params_dict = {
            'razorpay_order_id': order.razorpay_order_id,
            'razorpay_payment_id': order.razorpay_payment_id,
            'razorpay_signature': order.razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            order.payment_mode = 'Online Payment'
            order.amount_due = 0
            order.amount_paid = order.total
            order.save()

            # Send an email confirmation to the user
            return Response({"message": "Payment verified successfully"}, status=status.HTTP_200_OK)
        except razorpay.errors.SignatureVerificationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


######## End of Verify Payment ################

######## Addresses ##########

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address', 'city', 'state', 'pincode', 'phone']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user  # Assign the user from the request
        return super().create(validated_data)

class DeleteAddressSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class AddressesView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    
    def delete(self, request):
        serializer = DeleteAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = Address.objects.get(id=serializer.validated_data['id'])
        address.delete()
        return Response(serializer.data)


######End of Addresses #######




