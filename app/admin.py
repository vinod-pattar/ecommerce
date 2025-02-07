from django.contrib import admin
from .models import Category, Seller, Product, Cart, CartItem, Address, Enquiry, Order, OrderItem, Profile
from django.contrib.auth.models import User

# Register your models here.


class ProductInlineAdmin(admin.TabularInline):
    model = Product
    extra=0

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'image')
    search_fields = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug')
        }),
        ('Details', {
            'fields': ('description', )
        }),
    )
    inlines = [ProductInlineAdmin]

admin.site.register(Category, CategoryAdmin)




class SellerAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'image')
    search_fields = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'user')
        }),
        ('Details', {
            'fields': ('description',)
        }),
    )

    inlines = [ProductInlineAdmin]

    
    
admin.site.register(Seller, SellerAdmin)


class PriceRangeFilter(admin.SimpleListFilter):
    title = 'price range'  # Display name
    parameter_name = 'price_range'  # Query parameter in the URL

    def lookups(self, request, model_admin):
        return [
            ('low', 'Low (Under 500)'),
            ('mid', 'Mid (500 - 1000)'),
            ('high', 'High (Above 1500)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(price__lt=500)
        elif self.value() == 'mid':
            return queryset.filter(price__gte=50, price__lte=1000)
        elif self.value() == 'high':
            return queryset.filter(price__gt=1500)
        

class CategoryDropdownFilter(admin.SimpleListFilter):
    title = 'category'  # Title displayed in the admin
    parameter_name = 'category'  # Query parameter name

    def lookups(self, request, model_admin):
        # Returns a list of tuples (value, label) for the dropdown
        results = Category.objects.all()

        return [(category.id, category.name) for category in Category.objects.all()]

    def queryset(self, request, queryset):
        # Filters the queryset based on the selected value
        if self.value():
            return queryset.filter(category_id=self.value())
        return queryset
    
        
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'price', 'image', 'category_name', 'seller_name')
    search_fields = ('name',)
    # readonly_fields = ('slug', )
    list_filter = (CategoryDropdownFilter, 'seller', PriceRangeFilter)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug',  'image', 'user')
        }),
        ('Details', {
            'fields': ('description', 'price', 'category', 'seller')
        }),
    )

    def category_name(self, obj):
        return obj.category.name
    
    category_name.short_description = 'Category'

    def seller_name(self, obj):
        return obj.seller.name
    
    seller_name.short_description = 'Seller'
    


class OrderItemInlineAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'date', 'total', 'payment_mode', 'amount_paid', 'amount_due', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'status')
    search_fields = ('user', 'status')
    readonly_fields = ('user', 'date', 'total', 'payment_mode', 'amount_paid', 'amount_due', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',)
    list_filter = ('status', 'user')

    inlines = [OrderItemInlineAdmin]


    # def has_add_permission(self, request):
    #     return False


admin.site.register(Order, OrderAdmin)


class ProfileInlineAdmin(admin.TabularInline):
    model = Profile
    extra=0


admin.site.unregister(User)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'get_dob')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Details', {
            'fields': ('is_staff', 'is_active', 'date_joined')
        }),
    )

    inlines = [ProfileInlineAdmin]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def get_dob(self, obj):
        return obj.profile.dob
    
    get_dob.short_description = 'Date of Birth'


admin.site.register(User, UserAdmin)



class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'city', 'state', 'country', 'pincode', 'phone')
    search_fields = ('user__email', 'address', 'city', 'state', 'country', 'pincode', 'phone')
    list_filter = (('user', admin.RelatedOnlyFieldListFilter), 'city')

    autocomplete_fields = ['user']

admin.site.register(Address, AddressAdmin)


class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'message', 'date')
    search_fields = ('user__email', 'subject', 'message')
    list_filter = (('user', admin.RelatedOnlyFieldListFilter), 'date')
    readonly_fields = ('user', 'subject', 'message', 'date')

    autocomplete_fields = ['user']

admin.site.register(Enquiry, EnquiryAdmin)


