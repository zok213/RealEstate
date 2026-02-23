"""Check router endpoints."""
from api.routes.optimization_routes import router

print(f"Router: {router}")
print(f"Routes count: {len(router.routes)}")
for route in router.routes:
    print(f"  - {route.methods} {route.path}")
