from django.urls import path

from dentist.views import (AboutView, AppointmentView,
    ContactView,
    DepartmentListView,
    DepartmentDetailView,
    DoctorListView,
    DoctorDetailView,
    IndexView,
    ServiceListView,
    ServiceDetailView,
    TestimonialsView
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about"),
    path("appointment/", AppointmentView.as_view(), name="appointment"),
    path("contact/", ContactView.as_view(), name="contact"),

    # Bo'limlar
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/<slug:slug>/', DepartmentDetailView.as_view(), name='department_detail'),

    # Xizmatlar
    path("services/", ServiceListView.as_view(), name="services"),
    path("services/<slug:slug>/", ServiceDetailView.as_view(), name="service_detail"),

    # Shifokorlar
    path("doctors/", DoctorListView.as_view(), name="doctors"),
    path("doctor/<slug:slug>/", DoctorDetailView.as_view(), name="doctor_detail"),
    path("testimonials/", TestimonialsView.as_view(), name="testimonials"),
]