"""Check app routes."""
import sys  
sys.path.insert(0, '.')

from main import app

print(f"App: {app}")
print(f"Routes:") 
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  {route.methods} {route.path}")
