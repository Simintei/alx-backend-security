from django.shortcuts import render
from django.http import JsonResponse
from ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_authenticated(request):
    """
    Login endpoint with 10 requests/minute limit for authenticated users.
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            return JsonResponse({'message': 'Authenticated login successful'})
        else:
            return JsonResponse({'error': 'You are not logged in'}, status=401)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_anonymous(request):
    """
    Login endpoint with 5 requests/minute limit for anonymous users.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # simulate authentication
        if username == "admin" and password == "password":
            return JsonResponse({'message': 'Login success'})
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)
