from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from bookings.models import Booking
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required
def index(request):
    """Chat index view"""
    # Get bookings for current user
    if hasattr(request.user, 'agent'):
        bookings_list = Booking.objects.filter(quote__customer=request.user)
    else:
        bookings_list = Booking.objects.filter(customer=request.user)
    
    context = {
        'bookings': bookings_list,
        'user': request.user,
    }
    
    return render(request, 'chat/index.html', context)

@login_required
def chat_history(request, booking_id):
    """Get chat history for a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if (hasattr(request.user, 'agent') and booking.quote.customer.user != request.user) or \
       (not hasattr(request.user, 'agent') and booking.customer != request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get chat messages for this booking
    from .models import ChatMessage
    messages = ChatMessage.objects.filter(booking=booking).order_by('created_at')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender_type,
            'content': msg.content,
            'timestamp': msg.created_at.isoformat(),
        })
    
    return JsonResponse({'messages': messages_data})

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, booking_id):
    """Send a chat message"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    if (hasattr(request.user, 'agent') and booking.quote.customer.user != request.user) or \
       (not hasattr(request.user, 'agent') and booking.customer != request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Message content is required'}, status=400)
        
        from .models import ChatMessage
        
        # Determine sender type
        if hasattr(request.user, 'agent'):
            sender_type = 'agent'
            sender_name = request.user.get_full_name() or request.user.username
        else:
            sender_type = 'customer'
            sender_name = request.user.get_full_name() or request.user.username
        
        # Create message
        message = ChatMessage.objects.create(
            booking=booking,
            sender_type=sender_type,
            content=content,
            sender_name=sender_name
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': message.sender_type,
                'content': message.content,
                'timestamp': message.created_at.isoformat(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_chat(request):
    """API endpoint for chat (for real-time chat with WebSocket)"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'get_messages':
            booking_id = data.get('booking_id')
            booking = get_object_or_404(Booking, id=booking_id)
            
            # Check permissions
            if (hasattr(request.user, 'agent') and booking.quote.customer.user != request.user) or \
               (not hasattr(request.user, 'agent') and booking.customer != request.user):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            from .models import ChatMessage
            messages = ChatMessage.objects.filter(booking=booking).order_by('created_at')
            
            messages_data = []
            for msg in messages:
                messages_data.append({
                    'id': msg.id,
                    'sender': msg.sender_type,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                })
            
            return JsonResponse({'messages': messages_data})
        
        elif action == 'send_message':
            booking_id = data.get('booking_id')
            content = data.get('content', '').strip()
            
            if not content:
                return JsonResponse({'error': 'Message content is required'}, status=400)
            
            booking = get_object_or_404(Booking, id=booking_id)
            
            # Check permissions
            if (hasattr(request.user, 'agent') and booking.quote.customer.user != request.user) or \
               (not hasattr(request.user, 'agent') and booking.customer != request.user):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            from .models import ChatMessage
            
            # Determine sender type
            if hasattr(request.user, 'agent'):
                sender_type = 'agent'
                sender_name = request.user.get_full_name() or request.user.username
            else:
                sender_type = 'customer'
                sender_name = request.user.get_full_name() or request.user.username
            
            # Create message
            message = ChatMessage.objects.create(
                booking=booking,
                sender_type=sender_type,
                content=content,
                sender_name=sender_name
            )
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'sender': message.sender_type,
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                }
            })
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
