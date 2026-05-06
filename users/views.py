from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .models import CustomUser, FriendRequest
from .forms import LoginForm, ProfileUpdateForm, RegisterForm, UserUpdateForm


def home_view(request):
    context = {}
    if request.user.is_authenticated:
        from recipes.models import Recipe  # noqa: PLC0415

        friends_ids = request.user.friends.values_list('id', flat=True)
        feed_qs = (
            Recipe.objects.select_related('author')
            .prefetch_related('ingredients')
            .filter(Q(author=request.user) | Q(author_id__in=friends_ids))
            .order_by('-created_at')
        )
        paginator = Paginator(feed_qs, 6)
        page_obj = paginator.get_page(request.GET.get('page'))
        context['page_obj'] = page_obj
        context['feed_recipes'] = page_obj.object_list
        context['feed_total'] = feed_qs.count()
    return render(request, 'home.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm(request)

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

    return render(request, 'users/logout.html')


@login_required
def profile_view(request):
    return render(
        request,
        'users/profile.html',
        {
            'profile_user': request.user,
            'is_own_profile': True,
            'can_view_diary_info': True,
        },
    )


@login_required
def user_profile_view(request, username):
    profile_user = CustomUser.objects.filter(username=username).select_related('profile').first()
    if profile_user is None:
        return redirect('find_friends')

    if profile_user == request.user:
        return redirect('profile')

    is_friend = request.user.friends.filter(pk=profile_user.pk).exists()
    outgoing_request_sent = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=profile_user,
        status=FriendRequest.STATUS_PENDING,
    ).exists()
    can_view_diary_info = profile_user.profile.show_diary_to_friends and is_friend

    context = {
        'profile_user': profile_user,
        'is_own_profile': False,
        'is_friend': is_friend,
        'outgoing_request_sent': outgoing_request_sent,
        'can_view_diary_info': can_view_diary_info,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/edit_profile.html', context)


@login_required
def find_friends_view(request):
    query = request.GET.get('q', '').strip()
    users = CustomUser.objects.exclude(pk=request.user.pk).order_by('username')

    if query:
        users = users.filter(username__icontains=query)

    sent_request_ids = set(
        FriendRequest.objects.filter(
            from_user=request.user,
            status=FriendRequest.STATUS_PENDING,
        ).values_list('to_user_id', flat=True)
    )
    friend_ids = set(request.user.friends.values_list('id', flat=True))

    context = {
        'users': users,
        'query': query,
        'sent_request_ids': sent_request_ids,
        'friend_ids': friend_ids,
    }
    return render(request, 'users/find_friends.html', context)


@login_required
def add_friend_view(request, user_id):
    if request.method != 'POST':
        return HttpResponseForbidden('Only POST requests are allowed.')

    to_user = CustomUser.objects.filter(pk=user_id).first()
    if to_user is None or to_user == request.user:
        return redirect('find_friends')

    if request.user.friends.filter(pk=to_user.pk).exists():
        messages.info(request, 'Этот пользователь уже у вас в друзьях.')
        return redirect('find_friends')

    FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={'status': FriendRequest.STATUS_PENDING},
    )
    messages.success(request, 'Заявка в друзья отправлена.')
    return redirect('find_friends')


@login_required
def remove_friend_view(request, user_id):
    if request.method != 'POST':
        return HttpResponseForbidden('Only POST requests are allowed.')

    friend = CustomUser.objects.filter(pk=user_id).first()
    if friend is None or friend == request.user:
        return redirect('friends_list')

    if request.user.friends.filter(pk=friend.pk).exists():
        request.user.friends.remove(friend)
        friend.friends.remove(request.user)
        messages.success(request, 'Пользователь удалён из друзей.')
    else:
        messages.info(request, 'Этот пользователь уже не находится у вас в друзьях.')

    return redirect('friends_list')


@login_required
def friends_list_view(request):
    friends = request.user.friends.all().order_by('username')
    return render(request, 'users/friends_list.html', {'friends': friends})


@login_required
def friend_requests_view(request):
    incoming_requests = FriendRequest.objects.filter(
        to_user=request.user,
        status=FriendRequest.STATUS_PENDING,
    )
    outgoing_requests = FriendRequest.objects.filter(
        from_user=request.user,
        status=FriendRequest.STATUS_PENDING,
    )
    context = {
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
    }
    return render(request, 'users/friend_requests.html', context)


@login_required
def respond_friend_request_view(request, request_id, action):
    if request.method != 'POST':
        return HttpResponseForbidden('Only POST requests are allowed.')

    friend_request = FriendRequest.objects.filter(
        pk=request_id,
        to_user=request.user,
        status=FriendRequest.STATUS_PENDING,
    ).first()

    if friend_request is None:
        return redirect('friend_requests')

    if action == 'accept':
        friend_request.status = FriendRequest.STATUS_ACCEPTED
        friend_request.save(update_fields=['status'])
        request.user.friends.add(friend_request.from_user)
        messages.success(request, 'Заявка принята.')
    elif action == 'reject':
        friend_request.status = FriendRequest.STATUS_REJECTED
        friend_request.save(update_fields=['status'])
        messages.info(request, 'Заявка отклонена.')

    return redirect('friend_requests')
