import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def json_error(message, status=400):
    return JsonResponse({'success': False, 'error': message}, status=status)


def parse_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    return request.POST


def is_json_request(request):
    return request.content_type == 'application/json'


def render_page(request, template_name, context=None):
    return render(request, template_name, context or {})


@csrf_exempt
def signup(request):
    if request.method == 'GET':
        return render_page(request, 'accounts/signup.html')

    data = parse_request_data(request)
    if data is None:
        return json_error('Invalid JSON payload') if is_json_request(request) else render_page(request, 'accounts/signup.html', {'error_message': 'Invalid data'})

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        message = 'username, email, and password are required'
        return json_error(message) if is_json_request(request) else render_page(request, 'accounts/signup.html', {'error_message': message})

    if User.objects.filter(username=username).exists():
        message = 'Username already exists'
        return json_error(message) if is_json_request(request) else render_page(request, 'accounts/signup.html', {'error_message': message})

    if User.objects.filter(email=email).exists():
        message = 'Email already exists'
        return json_error(message) if is_json_request(request) else render_page(request, 'accounts/signup.html', {'error_message': message})

    try:
        validate_password(password)
    except ValidationError as exc:
        message = ' '.join(exc.messages)
        return json_error(message) if is_json_request(request) else render_page(request, 'accounts/signup.html', {'error_message': message})

    user = User.objects.create_user(username=username, email=email, password=password)
    if is_json_request(request):
        return JsonResponse({'success': True, 'message': 'User created', 'user': {'id': user.id, 'username': user.username, 'email': user.email}})

    return render_page(request, 'accounts/signup.html', {'success_message': 'User created successfully. You can now log in.'})


@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        return render_page(request, 'accounts/login.html')

    data = parse_request_data(request)
    if data is None:
        return json_error('Invalid JSON payload') if is_json_request(request) else render_page(request, 'accounts/login.html', {'error_message': 'Invalid data'})

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        message = 'username and password are required'
        return json_error(message) if is_json_request(request) else render_page(request, 'accounts/login.html', {'error_message': message})

    user = authenticate(request, username=username, password=password)
    if user is None:
        message = 'Invalid credentials'
        return json_error(message, status=401) if is_json_request(request) else render_page(request, 'accounts/login.html', {'error_message': message})

    login(request, user)
    if is_json_request(request):
        return JsonResponse({'success': True, 'message': 'Logged in', 'user': {'id': user.id, 'username': user.username, 'email': user.email}})

    return render_page(request, 'accounts/login.html', {'success_message': 'Logged in successfully.'})


@csrf_exempt
def logout_view(request):
    if request.method == 'GET':
        return render_page(request, 'accounts/logout.html')

    if not request.user.is_authenticated:
        message = 'Not authenticated'
        return json_error(message, status=401) if is_json_request(request) else render_page(request, 'accounts/logout.html', {'error_message': message})

    logout(request)
    if is_json_request(request):
        return JsonResponse({'success': True, 'message': 'Logged out'})

    return render_page(request, 'accounts/logout.html', {'success_message': 'Logged out successfully.'})


@csrf_exempt
def reset_password(request):
    if request.method == 'GET':
        return render_page(request, 'accounts/reset_password.html')

    data = parse_request_data(request)
    if data is None:
        return json_error('Invalid JSON payload') if is_json_request(request) else render_page(request, 'accounts/reset_password.html', {'error_message': 'Invalid data'})

    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        message = 'email and new_password are required'
        return json_error(message) if is_json_request(request) else render_page(request, 'accounts/reset_password.html', {'error_message': message})

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        message = 'User with this email does not exist'
        return json_error(message, status=404) if is_json_request(request) else render_page(request, 'accounts/reset_password.html', {'error_message': message})

    try:
        validate_password(new_password, user=user)
    except ValidationError as exc:
        message = ' '.join(exc.messages)
        return json_error(message) if is_json_request(request) else render_page(request, 'accounts/reset_password.html', {'error_message': message})

    user.set_password(new_password)
    user.save()

    if is_json_request(request):
        return JsonResponse({'success': True, 'message': 'Password reset successfully'})

    return render_page(request, 'accounts/reset_password.html', {'success_message': 'Password reset successfully.'})
