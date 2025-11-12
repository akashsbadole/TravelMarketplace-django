from django.db import models
from django.conf import settings

class PaymentMethod(models.Model):
    METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=METHOD_CHOICES)
    
    # Method specific details
    paypal_email = models.EmailField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    card_type = models.CharField(max_length=50, blank=True, null=True)
    card_expiry = models.CharField(max_length=10, blank=True, null=True)
    
    # Metadata
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    provider_token = models.CharField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_method_type_display()}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    TYPE_CHOICES = [
        ('booking_payment', 'Booking Payment'),
        ('agent_payout', 'Agent Payout'),
        ('commission_payment', 'Commission Payment'),
        ('refund', 'Refund'),
        ('chargeback', 'Chargeback'),
        ('fee', 'Fee'),
    ]
    
    # Core Information
    transaction_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    
    # Transaction Details
    transaction_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    # Payment Method Information
    payment_method = models.CharField(max_length=50)
    payment_gateway = models.CharField(max_length=50)  # PayPal, Stripe, etc.
    gateway_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Gateway Specific Fields
    paypal_payment_id = models.CharField(max_length=200, blank=True, null=True)
    paypal_payer_id = models.CharField(max_length=200, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True, null=True)
    stripe_charge_id = models.CharField(max_length=200, blank=True, null=True)
    
    # Fee Information
    processing_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    description = models.TextField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    refund_reason = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Refund Information
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_partial_refund = models.BooleanField(default=False)
    original_transaction = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='refunds')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency}"
    
    def calculate_net_amount(self):
        """Calculate net amount after fees"""
        self.net_amount = self.amount - self.processing_fee - self.platform_fee
        return self.net_amount

class PayoutRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, related_name='payout_requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Bank Details
    bank_account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=200)
    bank_branch = models.CharField(max_length=200)
    bank_ifsc_code = models.CharField(max_length=20)
    bank_account_holder_name = models.CharField(max_length=200)
    
    # Status and Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name='payout_requests')
    
    # Admin Processing
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payouts')
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Payout Request {self.id} - {self.agent.company_name} - {self.amount} {self.currency}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    INVOICE_TYPE_CHOICES = [
        ('booking', 'Booking Invoice'),
        ('commission', 'Commission Invoice'),
        ('payout', 'Payout Invoice'),
        ('refund', 'Refund Invoice'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    agent = models.ForeignKey('agents.Agent', on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Financial Details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Dates
    invoice_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Billing Information
    billing_name = models.CharField(max_length=200)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20, blank=True, null=True)
    billing_address = models.TextField()
    
    # Items
    items = models.JSONField(default=list, help_text="List of invoice items")
    
    # Payment Information
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)
    
    # File
    invoice_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.email}"
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        import datetime
        date_str = datetime.date.today().strftime("%Y%m%d")
        last_invoice = Invoice.objects.filter(invoice_number__startswith=f"INV{date_str}").order_by('-invoice_number').first()
        if last_invoice:
            last_num = int(last_invoice.invoice_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        return f"INV{date_str}{new_num:04d}"

class PaymentSettings(models.Model):
    # PayPal Settings
    paypal_client_id = models.CharField(max_length=500, blank=True, null=True)
    paypal_client_secret = models.CharField(max_length=500, blank=True, null=True)
    paypal_mode = models.CharField(max_length=20, choices=[('sandbox', 'Sandbox'), ('live', 'Live')], default='sandbox')
    
    # Stripe Settings
    stripe_public_key = models.CharField(max_length=500, blank=True, null=True)
    stripe_secret_key = models.CharField(max_length=500, blank=True, null=True)
    stripe_webhook_secret = models.CharField(max_length=500, blank=True, null=True)
    
    # General Settings
    default_currency = models.CharField(max_length=3, default='USD')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.02)
    minimum_payout_amount = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    
    # Processing Fees
    payment_processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.90)
    payment_processing_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0.30)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Payment Settings"
