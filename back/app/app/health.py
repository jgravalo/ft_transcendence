from django.http import HttpResponse, JsonResponse
from django.db import connections
from django.db.utils import OperationalError

def health_check(request):
    try:
        # Verifica la conexión a la base de datos
        db_conn = connections['default']
        db_conn.cursor()
        return JsonResponse({
            "status": "healthy",
            "database": "connected"
        })
    except OperationalError:
        return JsonResponse({
            "status": "unhealthy",
            "database": "disconnected"
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500) 