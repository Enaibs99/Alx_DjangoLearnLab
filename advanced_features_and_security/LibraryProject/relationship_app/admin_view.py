
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render
from .models import UserProfile

def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Admin'

def is_librarian(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Librarian'

def is_member(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Member'


@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    return render(request, 'admin_view.html')
