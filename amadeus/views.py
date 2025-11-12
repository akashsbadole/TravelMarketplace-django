from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Airport, Airline, Aircraft, FlightSearch, FlightOffer, FlightSegment,
    Hotel, HotelSearch, HotelOffer, PointOfInterest, AmadeusAPIConfiguration
)
from .services import AmadeusAPIService, AmadeusDataProcessor
from .forms import FlightSearchForm, HotelSearchForm


@login_required
def flight_search(request):
    """Flight search page"""
    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            try:
                # Create flight search record
                search = FlightSearch.objects.create(
                    user=request.user,
                    origin=form.cleaned_data['origin'],
                    destination=form.cleaned_data['destination'],
                    departure_date=form.cleaned_data['departure_date'],
                    return_date=form.cleaned_data.get('return_date'),
                    adults=form.cleaned_data['adults'],
                    children=form.cleaned_data['children'],
                    infants=form.cleaned_data['infants'],
                    cabin_class=form.cleaned_data['cabin_class'],
                    direct_flights_only=form.cleaned_data['direct_flights_only'],
                    max_price=form.cleaned_data['max_price']
                )
                
                # Add preferred airlines
                if form.cleaned_data['preferred_airlines']:
                    search.preferred_airlines.set(form.cleaned_data['preferred_airlines'])
                
                # Search flights using Amadeus API
                api_service = AmadeusAPIService()
                response = api_service.search_flights(
                    origin=search.origin.iata_code,
                    destination=search.destination.iata_code,
                    departure_date=search.departure_date,
                    return_date=search.return_date,
                    adults=search.adults,
                    children=search.children,
                    infants=search.infants,
                    cabin_class=search.cabin_class,
                    direct_flights_only=search.direct_flights_only,
                    max_price=search.max_price,
                    airlines=[airline.iata_code for airline in search.preferred_airlines.all()]
                )
                
                # Process and save results
                search.search_results = response
                search.results_count = len(response.get('data', []))
                search.is_completed = True
                search.save()
                
                # Process flight offers
                AmadeusDataProcessor.process_flight_search_response(response, search)
                
                messages.success(request, f"Found {search.results_count} flight options!")
                return redirect('amadeus:flight_results', search_id=search.id)
                
            except Exception as e:
                messages.error(request, f"Flight search failed: {str(e)}")
    else:
        form = FlightSearchForm()
    
    return render(request, 'amadeus/flight_search.html', {
        'form': form,
        'page_title': 'Search Flights'
    })


@login_required
def flight_results(request, search_id):
    """Display flight search results"""
    search = get_object_or_404(FlightSearch, id=search_id, user=request.user)
    offers = search.flight_offers.all().prefetch_related('segments__airline', 'segments__departure_airport', 'segments__arrival_airport')
    
    # Get unique airlines for filtering
    airlines = Airline.objects.filter(segments__offer__in=offers).distinct()
    
    # Get price range for filtering
    prices = [offer.price_total for offer in offers]
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 1000
    
    return render(request, 'amadeus/flight_results.html', {
        'search': search,
        'offers': offers,
        'airlines': airlines,
        'min_price': min_price,
        'max_price': max_price,
        'page_title': f'Flights from {search.origin.iata_code} to {search.destination.iata_code}'
    })


@login_required
def flight_detail(request, offer_id):
    """Display detailed flight information"""
    offer = get_object_or_404(FlightOffer, id=offer_id)
    segments = offer.segments.all().order_by('segment_number')
    
    # Get pricing details
    try:
        api_service = AmadeusAPIService()
        pricing_response = api_service.get_flight_price([offer.offer_id])
        offer.raw_data.update(pricing_response)
        offer.save()
    except Exception as e:
        messages.warning(request, f"Could not fetch latest pricing: {str(e)}")
    
    return render(request, 'amadeus/flight_detail.html', {
        'offer': offer,
        'segments': segments,
        'page_title': f'Flight Details - {offer.offer_id}'
    })


@login_required
def hotel_search(request):
    """Hotel search page"""
    if request.method == 'POST':
        form = HotelSearchForm(request.POST)
        if form.is_valid():
            try:
                # Create hotel search record
                search = HotelSearch.objects.create(
                    user=request.user,
                    city_code=form.cleaned_data['city_code'],
                    check_in_date=form.cleaned_data['check_in_date'],
                    check_out_date=form.cleaned_data['check_out_date'],
                    adults=form.cleaned_data['adults'],
                    children=form.cleaned_data['children'],
                    room_quantity=form.cleaned_data['room_quantity'],
                    price_range=form.cleaned_data.get('price_range'),
                    rating=form.cleaned_data.get('rating'),
                    amenities=form.cleaned_data.get('amenities', [])
                )
                
                # Search hotels using Amadeus API
                api_service = AmadeusAPIService()
                response = api_service.search_hotels(
                    city_code=search.city_code,
                    check_in_date=search.check_in_date,
                    check_out_date=search.check_out_date,
                    adults=search.adults,
                    room_quantity=search.room_quantity,
                    price_range=search.price_range,
                    rating=search.rating,
                    amenities=search.amenities
                )
                
                # Process and save results
                search.search_results = response
                search.results_count = len(response.get('data', []))
                search.is_completed = True
                search.save()
                
                # Process hotel offers
                AmadeusDataProcessor.process_hotel_search_response(response, search)
                
                messages.success(request, f"Found {search.results_count} hotel options!")
                return redirect('amadeus:hotel_results', search_id=search.id)
                
            except Exception as e:
                messages.error(request, f"Hotel search failed: {str(e)}")
    else:
        form = HotelSearchForm()
    
    return render(request, 'amadeus/hotel_search.html', {
        'form': form,
        'page_title': 'Search Hotels'
    })


@login_required
def hotel_results(request, search_id):
    """Display hotel search results"""
    search = get_object_or_404(HotelSearch, id=search_id, user=request.user)
    offers = search.hotel_offers.all().select_related('hotel')
    
    # Get unique hotel ratings for filtering
    ratings = set(offer.hotel.rating for offer in offers if offer.hotel.rating)
    
    # Get price range for filtering
    prices = [offer.price_total for offer in offers]
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 1000
    
    return render(request, 'amadeus/hotel_results.html', {
        'search': search,
        'offers': offers,
        'ratings': sorted(ratings),
        'min_price': min_price,
        'max_price': max_price,
        'page_title': f'Hotels in {search.city_code}'
    })


@login_required
def hotel_detail(request, offer_id):
    """Display detailed hotel information"""
    offer = get_object_or_404(HotelOffer, id=offer_id)
    hotel = offer.hotel
    
    # Get additional hotel details
    try:
        api_service = AmadeusAPIService()
        details_response = api_service.get_hotel_details(hotel.hotel_id)
        hotel.raw_data.update(details_response)
        hotel.save()
        
        # Get hotel reviews
        reviews_response = api_service.get_hotel_reviews(hotel.hotel_id)
        hotel.raw_data['reviews'] = reviews_response
        hotel.save()
    except Exception as e:
        messages.warning(request, f"Could not fetch latest hotel details: {str(e)}")
    
    # Get nearby points of interest
    nearby_pois = []
    if hotel.latitude and hotel.longitude:
        try:
            api_service = AmadeusAPIService()
            pois_response = api_service.search_points_of_interest(
                latitude=float(hotel.latitude),
                longitude=float(hotel.longitude),
                radius=2
            )
            nearby_pois = pois_response.get('data', [])[:5]  # Limit to 5 POIs
        except Exception as e:
            pass  # Don't show error for POIs
    
    return render(request, 'amadeus/hotel_detail.html', {
        'offer': offer,
        'hotel': hotel,
        'nearby_pois': nearby_pois,
        'page_title': f'{hotel.name} - Hotel Details'
    })


@login_required
def flight_inspiration(request):
    """Flight inspiration based on budget"""
    if request.method == 'POST':
        origin = request.POST.get('origin')
        budget = request.POST.get('budget')
        departure_date = request.POST.get('departure_date')
        
        if not origin or not budget:
            messages.error(request, "Please provide origin and budget")
            return render(request, 'amadeus/flight_inspiration.html', {
                'page_title': 'Flight Inspiration'
            })
        
        try:
            api_service = AmadeusAPIService()
            
            # Parse dates
            dep_date = None
            if departure_date:
                dep_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            
            response = api_service.search_flight_inspiration(
                origin=origin,
                budget=budget,
                departure_date=dep_date
            )
            
            destinations = response.get('data', [])
            
            return render(request, 'amadeus/flight_inspiration_results.html', {
                'origin': origin,
                'budget': budget,
                'destinations': destinations,
                'page_title': 'Flight Inspiration Results'
            })
            
        except Exception as e:
            messages.error(request, f"Flight inspiration search failed: {str(e)}")
    
    return render(request, 'amadeus/flight_inspiration.html', {
        'page_title': 'Flight Inspiration'
    })


@csrf_exempt
@require_POST
def airport_autocomplete(request):
    """Airport autocomplete for search forms"""
    query = request.POST.get('query', '')
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    try:
        api_service = AmadeusAPIService()
        response = api_service.search_airports(query)
        
        suggestions = []
        for location in response.get('data', []):
            if location.get('subType') in ['AIRPORT', 'CITY']:
                suggestions.append({
                    'iata_code': location.get('iataCode'),
                    'name': location.get('name'),
                    'city': location.get('address', {}).get('cityName'),
                    'country': location.get('address', {}).get('countryName'),
                    'sub_type': location.get('subType')
                })
        
        return JsonResponse({'suggestions': suggestions[:10]})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def search_history(request):
    """Display user's search history"""
    flight_searches = FlightSearch.objects.filter(user=request.user).order_by('-created_at')[:10]
    hotel_searches = HotelSearch.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    return render(request, 'amadeus/search_history.html', {
        'flight_searches': flight_searches,
        'hotel_searches': hotel_searches,
        'page_title': 'Search History'
    })


@login_required
def agent_quote_builder(request, requirement_id):
    """Enhanced quote builder with Amadeus data for agents"""
    from requirements.models import Requirement
    from agents.models import Agent
    
    # Check if user is an agent
    try:
        agent = request.user.agent
    except Agent.DoesNotExist:
        messages.error(request, "Only agents can access this page")
        return redirect('dashboard:dashboard')
    
    requirement = get_object_or_404(Requirement, id=requirement_id)
    
    # Check if requirement is for flight or hotel service
    if requirement.service_type.name.lower() not in ['flight', 'hotel']:
        messages.error(request, "This feature is only available for flight and hotel requirements")
        return redirect('agents:requirement_detail', requirement_id)
    
    # Get Amadeus data for quote building
    amadeus_data = {}
    
    if requirement.service_type.name.lower() == 'flight':
        # Extract flight details from requirement
        origin = requirement.origin_city
        destination = requirement.destination_city
        departure_date = requirement.travel_date_start
        
        if origin and destination and departure_date:
            try:
                api_service = AmadeusAPIService()
                response = api_service.search_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=departure_date,
                    adults=requirement.adults or 1,
                    children=requirement.children or 0
                )
                amadeus_data['flights'] = response.get('data', [])
            except Exception as e:
                messages.warning(request, f"Could not fetch flight data: {str(e)}")
    
    elif requirement.service_type.name.lower() == 'hotel':
        # Extract hotel details from requirement
        city = requirement.destination_city
        check_in = requirement.travel_date_start
        check_out = requirement.travel_date_end
        
        if city and check_in and check_out:
            try:
                api_service = AmadeusAPIService()
                response = api_service.search_hotels(
                    city_code=city,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    adults=requirement.adults or 1,
                    room_quantity=requirement.rooms or 1
                )
                amadeus_data['hotels'] = response.get('data', [])
            except Exception as e:
                messages.warning(request, f"Could not fetch hotel data: {str(e)}")
    
    return render(request, 'amadeus/agent_quote_builder.html', {
        'requirement': requirement,
        'agent': agent,
        'amadeus_data': amadeus_data,
        'page_title': f'Quote Builder - {requirement.title}'
    })


def api_status(request):
    """Check Amadeus API status"""
    try:
        config = AmadeusAPIConfiguration.objects.filter(is_active=True).first()
        if not config:
            return JsonResponse({'status': 'error', 'message': 'No active API configuration'})
        
        api_service = AmadeusAPIService()
        
        # Test API connectivity
        token = api_service._get_access_token()
        
        # Get today's quota
        from django.utils import timezone
        today = timezone.now().date()
        from .models import APIQuota
        quota, _ = APIQuota.objects.get_or_create(
            date=today,
            defaults={'quota_limit': config.daily_quota_limit}
        )
        
        return JsonResponse({
            'status': 'success',
            'api_environment': config.environment,
            'quota_used': quota.total_requests,
            'quota_limit': config.daily_quota_limit,
            'quota_remaining': quota.quota_remaining,
            'token_valid': bool(token)
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})