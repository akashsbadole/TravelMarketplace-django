from django import forms
from django.utils import timezone
from .models import Airport, Airline, AmadeusAPIConfiguration


class FlightSearchForm(forms.Form):
    """Form for flight search"""
    origin = forms.ModelChoiceField(
        queryset=Airport.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'origin-select'}),
        label='From'
    )
    destination = forms.ModelChoiceField(
        queryset=Airport.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'destination-select'}),
        label='To'
    )
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date()
        }),
        label='Departure Date'
    )
    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date()
        }),
        label='Return Date (Optional)'
    )
    trip_type = forms.ChoiceField(
        choices=[
            ('round_trip', 'Round Trip'),
            ('one_way', 'One Way')
        ],
        initial='round_trip',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Trip Type'
    )
    adults = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 9}),
        label='Adults'
    )
    children = forms.IntegerField(
        min_value=0,
        max_value=8,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 8}),
        label='Children (2-11 years)'
    )
    infants = forms.IntegerField(
        min_value=0,
        max_value=4,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 4}),
        label='Infants (Under 2 years)'
    )
    cabin_class = forms.ChoiceField(
        choices=[
            ('ECONOMY', 'Economy'),
            ('PREMIUM_ECONOMY', 'Premium Economy'),
            ('BUSINESS', 'Business'),
            ('FIRST', 'First Class')
        ],
        initial='ECONOMY',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Cabin Class'
    )
    direct_flights_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Direct flights only'
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Enter maximum price'
        }),
        label='Maximum Price (USD)'
    )
    preferred_airlines = forms.ModelMultipleChoiceField(
        queryset=Airline.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Preferred Airlines'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['origin'].queryset = Airport.objects.filter(is_active=True).order_by('iata_code')
        self.fields['destination'].queryset = Airport.objects.filter(is_active=True).order_by('iata_code')
        self.fields['preferred_airlines'].queryset = Airline.objects.filter(is_active=True).order_by('name')
    
    def clean(self):
        cleaned_data = super().clean()
        departure_date = cleaned_data.get('departure_date')
        return_date = cleaned_data.get('return_date')
        trip_type = cleaned_data.get('trip_type')
        
        # Validate dates
        if departure_date and departure_date < timezone.now().date():
            raise forms.ValidationError("Departure date cannot be in the past")
        
        if trip_type == 'round_trip' and not return_date:
            raise forms.ValidationError("Return date is required for round trip")
        
        if return_date and return_date <= departure_date:
            raise forms.ValidationError("Return date must be after departure date")
        
        # Validate total passengers
        adults = cleaned_data.get('adults', 0)
        children = cleaned_data.get('children', 0)
        infants = cleaned_data.get('infants', 0)
        total_passengers = adults + children + infants
        
        if total_passengers > 9:
            raise forms.ValidationError("Total number of passengers cannot exceed 9")
        
        if adults < infants:
            raise forms.ValidationError("Number of adults must be at least equal to number of infants")
        
        return cleaned_data


class HotelSearchForm(forms.Form):
    """Form for hotel search"""
    city_code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'city-select',
            'placeholder': 'Enter city name or airport code'
        }),
        label='Destination'
    )
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date()
        }),
        label='Check-in Date'
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date()
        }),
        label='Check-out Date'
    )
    adults = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 9}),
        label='Adults'
    )
    children = forms.IntegerField(
        min_value=0,
        max_value=8,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 8}),
        label='Children'
    )
    room_quantity = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 9}),
        label='Number of Rooms'
    )
    price_range = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 50-200'
        }),
        label='Price Range (USD)'
    )
    rating = forms.DecimalField(
        required=False,
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'max': 5,
            'step': 0.5
        }),
        label='Minimum Rating'
    )
    amenities = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('POOL', 'Swimming Pool'),
            ('SPA', 'Spa'),
            ('GYM', 'Fitness Center'),
            ('PARKING', 'Parking'),
            ('WIFI', 'Free WiFi'),
            ('RESTAURANT', 'Restaurant'),
            ('BAR', 'Bar/Lounge'),
            ('BUSINESS_CENTER', 'Business Center'),
            ('PET_FRIENDLY', 'Pet Friendly'),
            ('AIRPORT_SHUTTLE', 'Airport Shuttle')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Amenities'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        price_range = cleaned_data.get('price_range')
        
        # Validate dates
        if check_in_date and check_in_date < timezone.now().date():
            raise forms.ValidationError("Check-in date cannot be in the past")
        
        if check_out_date and check_out_date <= check_in_date:
            raise forms.ValidationError("Check-out date must be after check-in date")
        
        # Validate price range
        if price_range:
            try:
                min_price, max_price = price_range.split('-')
                min_price = float(min_price.strip())
                max_price = float(max_price.strip())
                
                if min_price >= max_price:
                    raise forms.ValidationError("Minimum price must be less than maximum price")
                
                if min_price < 0 or max_price < 0:
                    raise forms.ValidationError("Prices must be positive numbers")
                    
            except (ValueError, AttributeError):
                raise forms.ValidationError("Price range must be in format: min-max (e.g., 50-200)")
        
        return cleaned_data


class FlightInspirationForm(forms.Form):
    """Form for flight inspiration search"""
    origin = forms.CharField(
        max_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'origin-select',
            'placeholder': 'Enter airport code',
            'maxlength': 3
        }),
        label='From'
    )
    budget = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Enter budget in USD'
        }),
        label='Budget (USD)'
    )
    departure_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date()
        }),
        label='Departure Date (Optional)'
    )
    duration = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 7-14'
        }),
        label='Trip Duration (days, Optional)'
    )
    destination_country_code = forms.CharField(
        required=False,
        max_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., US',
            'maxlength': 2
        }),
        label='Destination Country (Optional)'
    )
    
    def clean_origin(self):
        origin = self.cleaned_data.get('origin')
        if origin:
            origin = origin.upper()
            # Validate airport code exists
            if not Airport.objects.filter(iata_code=origin, is_active=True).exists():
                raise forms.ValidationError("Invalid airport code")
        return origin
    
    def clean_destination_country_code(self):
        country_code = self.cleaned_data.get('destination_country_code')
        if country_code:
            country_code = country_code.upper()
        return country_code
    
    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration:
            try:
                min_days, max_days = duration.split('-')
                min_days = int(min_days.strip())
                max_days = int(max_days.strip())
                
                if min_days >= max_days:
                    raise forms.ValidationError("Minimum days must be less than maximum days")
                
                if min_days < 1 or max_days < 1:
                    raise forms.ValidationError("Duration must be positive")
                    
            except (ValueError, AttributeError):
                raise forms.ValidationError("Duration must be in format: min-max (e.g., 7-14)")
        return duration


class APIConfigurationForm(forms.ModelForm):
    """Form for API configuration"""
    class Meta:
        model = AmadeusAPIConfiguration
        fields = ['name', 'api_key', 'api_secret', 'environment', 'daily_quota_limit', 'rate_limit_per_minute', 'is_active']
        widgets = {
            'api_key': forms.PasswordInput(attrs={'class': 'form-control'}),
            'api_secret': forms.PasswordInput(attrs={'class': 'form-control'}),
            'environment': forms.Select(attrs={'class': 'form-control'}),
            'daily_quota_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': 100}),
            'rate_limit_per_minute': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_daily_quota_limit(self):
        quota_limit = self.cleaned_data.get('daily_quota_limit')
        if quota_limit < 100:
            raise forms.ValidationError("Daily quota limit must be at least 100")
        return quota_limit
    
    def clean_rate_limit_per_minute(self):
        rate_limit = self.cleaned_data.get('rate_limit_per_minute')
        if rate_limit < 1:
            raise forms.ValidationError("Rate limit must be at least 1 per minute")
        return rate_limit


class AirportImportForm(forms.Form):
    """Form for importing airport data"""
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.json'}),
        label='Airport Data File'
    )
    file_type = forms.ChoiceField(
        choices=[
            ('csv', 'CSV File'),
            ('json', 'JSON File')
        ],
        initial='csv',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='File Type'
    )
    overwrite_existing = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Overwrite existing airports'
    )


class FlightFilterForm(forms.Form):
    """Form for filtering flight results"""
    airlines = forms.ModelMultipleChoiceField(
        queryset=Airline.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Airlines'
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Minimum Price'
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Maximum Price'
    )
    stops = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('0', 'Direct'),
            ('1', '1 Stop'),
            ('2', '2+ Stops')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Stops'
    )
    departure_time_range = forms.ChoiceField(
        choices=[
            ('', 'Any Time'),
            ('morning', 'Morning (6AM-12PM)'),
            ('afternoon', 'Afternoon (12PM-6PM)'),
            ('evening', 'Evening (6PM-12AM)'),
            ('night', 'Night (12AM-6AM)')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Departure Time'
    )
    arrival_time_range = forms.ChoiceField(
        choices=[
            ('', 'Any Time'),
            ('morning', 'Morning (6AM-12PM)'),
            ('afternoon', 'Afternoon (12PM-6PM)'),
            ('evening', 'Evening (6PM-12AM)'),
            ('night', 'Night (12AM-6AM)')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Arrival Time'
    )
    duration_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        label='Maximum Duration (hours)'
    )


class HotelFilterForm(forms.Form):
    """Form for filtering hotel results"""
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Minimum Price'
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Maximum Price'
    )
    rating = forms.DecimalField(
        required=False,
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'step': 0.5}),
        label='Minimum Rating'
    )
    amenities = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('POOL', 'Swimming Pool'),
            ('SPA', 'Spa'),
            ('GYM', 'Fitness Center'),
            ('PARKING', 'Parking'),
            ('WIFI', 'Free WiFi'),
            ('RESTAURANT', 'Restaurant'),
            ('BAR', 'Bar/Lounge'),
            ('BUSINESS_CENTER', 'Business Center'),
            ('PET_FRIENDLY', 'Pet Friendly'),
            ('AIRPORT_SHUTTLE', 'Airport Shuttle')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Amenities'
    )
    board_type = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('ROOM_ONLY', 'Room Only'),
            ('BREAKFAST', 'Breakfast Included'),
            ('HALF_BOARD', 'Half Board'),
            ('FULL_BOARD', 'Full Board'),
            ('ALL_INCLUSIVE', 'All Inclusive')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Board Type'
    )
    refundable = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Refundable Only'
    )