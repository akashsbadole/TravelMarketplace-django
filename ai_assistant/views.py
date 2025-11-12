from django.shortcuts import render
from django.http import JsonResponse
import json

def ai_chat(request):
    """AI chat interface view"""
    return render(request, 'ai_assistant/chat.html')

def ask_ai(request):
    """Handle AI requests and return responses"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Placeholder response - in a real app, this would call an AI service
            if 'hello' in user_message.lower() or 'hi' in user_message.lower():
                response = "Hello! I'm your AI travel assistant. How can I help you plan your trip today?"
            elif 'destination' in user_message.lower():
                response = "I can help you find the perfect destination! What kind of experience are you looking for? Beach, mountains, city, or cultural attractions?"
            elif 'budget' in user_message.lower():
                response = "Budget planning is important for any trip! What's your approximate budget range, and where are you planning to go?"
            else:
                response = f"I understand you're asking about: {user_message}. As your AI travel assistant, I'm here to help with travel planning, destination recommendations, and itinerary suggestions. Could you provide more details about what you'd like to know?"
            
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
