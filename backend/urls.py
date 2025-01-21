from django.urls import path
from .views import (home, profile,
                    add_surgery,
                    search_surgery_name,
                    search_surgery_type,
                    edit_surgery,
                    delete_surgery,
                    update_seq_number,
                    change_editable_surgeryday,
                    update_surgery_seq,
                    generate_pdf)
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginView.as_view(template_name='login.html', next_page='/'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('download-pdf/', generate_pdf, name='download_pdf'),
    path('profile/', profile, name='profile'),

    path('add_surgery/<int:branch_id>', add_surgery, name='add_surgery'),
    path('search_surgery_name/', search_surgery_name, name='search_surgery_name'),
    path('search_surgery_type/', search_surgery_type, name='search_surgery_type'),
    path('surgery/<int:surgery_id>/edit/', edit_surgery, name='edit_surgery'),
    path('surgery/<int:surgery_id>/delete/', delete_surgery, name='delete_surgery'),

    path('update_seq_number/', update_seq_number, name='update_seq_number'),

    path('editable/<int:surgeryday_id>/', change_editable_surgeryday, name='editable_change'),
    path('update_surgery_seq/', update_surgery_seq, name='update_surgery_seq'),
]
