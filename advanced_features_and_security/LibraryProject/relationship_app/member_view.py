
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render
from .models import UserProfile
from django.http import HttpResponse


def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Admin'

def is_librarian(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Librarian'

def is_member(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Member'

@user_passes_test(is_member)
@login_required
def member_dashboard(request):
    return render(request, 'member_view.html')
