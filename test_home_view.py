import os
import sys
import django

# Add project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_marketplace.settings')
django.setup()

from django.test import RequestFactory
from pages.views import home

# Create a mock request
factory = RequestFactory()
request = factory.get('/')

# Call the home view
try:
    response = home(request)
    print(f"Response status code: {response.status_code}")
    
    # Try to access rendered content
    if hasattr(response, 'content'):
        content = response.content.decode('utf-8')
        print("\nChecking rendered content for destinations and agents...")
        
        # Check for destination placeholders
        if 'Paris' in content or 'Tokyo' in content or 'New York' in content:
            print("[OK] Found destination names in content")
        else:
            print("[FAIL] Destination names not found in content")
            
        # Check for agent placeholders
        if 'Travel Experts' in content or 'Asia Adventures' in content:
            print("[OK] Found agent names in content")
        else:
            print("[FAIL] Agent names not found in content")
            
        # Check for fallback data
        if 'Paris' in content and 'Travel Experts Inc' in content:
            print("[OK] Using database data")
        elif 'Paris' in content and 'Travel Experts Inc' not in content:
            print("[INFO] Mixed data (destinations from DB, agents as fallback)")
        else:
            print("[INFO] Using fallback data for both")
    
    # Try to access context data if available
    try:
        if hasattr(response, 'context_data'):
            context = response.context_data
            print("\nContext data:")
            
            if 'featured_destinations' in context:
                print(f"Featured destinations count: {len(context['featured_destinations'])}")
                for dest in context['featured_destinations']:
                    print(f"  - {dest.get('name', 'Unknown')}")
            
            if 'featured_agents' in context:
                print(f"\nFeatured agents count: {len(context['featured_agents'])}")
                for agent in context['featured_agents']:
                    print(f"  - {agent.get('name', 'Unknown')}")
            
            if 'recent_blogs' in context:
                print(f"\nRecent blogs count: {len(context['recent_blogs'])}")
                for blog in context['recent_blogs']:
                    print(f"  - {blog.title if hasattr(blog, 'title') else 'Unknown'}")
        else:
            print("No context data available in response")
    except Exception as e:
        print(f"Error accessing context: {str(e)}")
        
except Exception as e:
    print(f"Error calling home view: {str(e)}")
    import traceback
    traceback.print_exc()