import os

from django.contrib import messages
from django.contrib.sites import requests
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.db import models

from dentist.forms import ContactForm
from dentist.models import Department, Service, Doctor, ContactMessage


# Create your views here.

class DepartmentListView(ListView):
    """Barcha faol bo'limlar ro'yxati"""
    model = Department
    template_name = "departments.html"
    context_object_name = "departments"

    def get_queryset(self):
        # Faqat faol bo'limlarni tartibi bo'yicha olamiz
        return Department.objects.filter(is_active=True).prefetch_related('doctors')


class DepartmentDetailView(DetailView):
    """Bitta bo'lim haqida to'liq malumot (dinamik)"""
    model = Department
    template_name = "department-details.html"
    context_object_name = "department"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Department.objects.filter(is_active=True).prefetch_related(
            'doctors', 'services', 'features', 'working_hours'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = self.object.services.filter(is_active=True)
        context['features'] = self.object.features.all()
        context['hours'] = self.object.working_hours.all()
        context['doctors'] = self.object.doctors.filter(is_available=True)
        return context


class ServiceListView(ListView):
    """Barcha xizmatlar ro'yxati"""
    model = Service
    template_name = "services.html"
    context_object_name = "services"

    def get_queryset(self):
        # Faqat faol xizmatlarni va ularga tegishli bo'limlarni so'rovda olamiz
        return Service.objects.filter(is_active=True).select_related('department').order_by('order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Statistika uchun
        context['total_services'] = Service.objects.filter(is_active=True).count()
        context['total_doctors'] = Doctor.objects.filter(is_available=True).count()
        return context


class ServiceDetailView(DetailView):
    """Bitta xizmat haqida batafsil ma'lumot"""
    model = Service
    template_name = "service-details.html"
    context_object_name = "service"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Service.objects.filter(is_active=True).select_related('department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # O'xshash xizmatlarni (shu bo'limdagi boshqa xizmatlar) ko'rsatish uchun
        context["related_services"] = Service.objects.filter(
            department=self.object.department,
            is_active=True
        ).exclude(id=self.object.id).order_by('order')[:3]

        # Bu bo'limdagi shifokorlar
        context["department_doctors"] = Doctor.objects.filter(
            department=self.object.department,
            is_available=True
        ).order_by('order')[:4]

        return context


class DoctorListView(ListView):
    """Barcha shifokorlar ro'yxati"""
    model = Doctor
    template_name = "doctors.html"
    context_object_name = "doctors"

    def get_queryset(self):
        # Faqat mavjud shifokorlarni olamiz
        queryset = Doctor.objects.filter(is_available=True).select_related('department').order_by('order', 'last_name')

        # Bo'lim bo'yicha filter
        department_id = self.request.GET.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        # Qidiruv
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(specialization__icontains=search) |
                models.Q(bio__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Bo'limlar ro'yxati (filter uchun)
        context['departments'] = Department.objects.filter(is_active=True).order_by('order')
        # Asosiy sahifadagi shifokorlar
        context['featured_doctors'] = Doctor.objects.filter(
            is_available=True,
            is_futured=True
        ).select_related('department').order_by('order')[:3]
        return context


class DoctorDetailView(DetailView):
    """Bitta shifokor haqida batafsil ma'lumot"""
    model = Doctor
    template_name = "doctor-details.html"
    context_object_name = "doctor"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Doctor.objects.filter(is_available=True).select_related('department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Shu bo'limdagi boshqa shifokorlar
        context["related_doctors"] = Doctor.objects.filter(
            department=self.object.department,
            is_available=True
        ).exclude(id=self.object.id).order_by('order')[:3]
        return context


class ContactView(TemplateView):
    """Bog'lanish vazifasi"""
    template_name = "contact.html"
    from_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        contact_message = form.save()

        message = (
            f"📩 <b>Yangi xabar (Bog'lanish)</b>\n\n"
            f"👤 Ism: {contact_message.name}\n"
            f"📞 Tel: {contact_message.phone}\n"
            f"📝 Mavzu: {contact_message.subject}\n"
            f"💬 Xabar: {contact_message.message}"
        )

        send_telegram_message(message)

        messages.success(self.request, f"Rahmat, {contact_message.name}! Xabaringiz qabul qilindi.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Xatolarni terminalda ko‘rish uchun
        print(form.errors)
        messages.error(self.request, "Iltimos, ma'lumotlarni to'g'ri kiriting.")
        return super().form_invalid(form)





class TestimonialsView(TemplateView):
    template_name = "testimonials.html"


class AboutView(TemplateView):
    template_name = "about.html"


class IndexView(TemplateView):
    template_name = "index.html"


class AppointmentView(TemplateView):
    template_name = "appointment.html"







def send_telegram_message(message):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=5)
        # Terminalda tekshirish uchun:
        print(f"Telegram status code: {response.status_code}")
        print(f"Telegram response: {response.text}")

        return response.status_code == 200
    except Exception as e:
        print(f"Telegram ulanish xatosi: {e}")
        return False
