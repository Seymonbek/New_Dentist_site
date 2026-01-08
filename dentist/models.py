from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from django.utils.text import slugify
from django.db import models
from django.urls import reverse


# Create your models here.


class Department(models.Model):
    """Klinika bo'limlari (Terapiya, Ortopediya, Ortodontiya va h.k.)"""
    name = models.CharField(max_length=200, verbose_name="Bo'lim nomi")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL Slug")
    icon =models.CharField(max_length=200, verbose_name="Icon class", default="fas fa-tooth")
    description = models.TextField(verbose_name="Qisqa ta'rif")
    full_description = models.TextField(verbose_name="To'liq ta'rif")
    image = models.ImageField(upload_to="departments/", verbose_name="Rasm", null=True, blank=True)

    is_active = models.BooleanField(default=True, verbose_name="Faol yoki faol emasligi")
    order = models.IntegerField(default=1, verbose_name="Ko'rsatish tartibi (kichik raqam birinchi)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    class Meta:
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug =slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('department_detail', kwargs={'slug': self.slug})


class DepartmentFeature(models.Model):
    """Bo'limning o'ziga xos afzalliklari (masalan: Zamonaviy lazer uskunalari)"""
    department = models.ForeignKey(Department, related_name='features', on_delete=models.CASCADE)
    text = models.CharField(max_length=200, verbose_name="Xususiyat matni")

    class Meta:
        verbose_name = "Bo'lim xususiyati"
        verbose_name_plural = "Bo'limlar xususiyatlari"

    def __str__(self):
        return f"{self.department.name} - {self.text}"

class WorkingHour(models.Model):
    """Bo'limning ish vaqtlari"""
    department = models.ForeignKey(Department, related_name='working_hours', on_delete=models.CASCADE)
    day_range = models.CharField(max_length=100, verbose_name="Kunlar (masalan: Dush-Juma)")
    time_range = models.CharField(max_length=100, verbose_name="Vaqt (masalan: 09:00 - 18:00)")

    class Meta:
        verbose_name = "Ish vaqti"
        verbose_name_plural = "Ish vaqtlari"

    def __str__(self):
        return f"{self.department.name}: {self.day_range} ({self.time_range})"


class Service(models.Model):
    """Klinika xizmatlari"""
    name = models.CharField(max_length=200, verbose_name="Xizmat nomi")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL Slug")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="services", verbose_name="Bo'lim")
    icon = models.CharField(max_length=200, verbose_name="Icon class", default="fas fa-tooth")

    description = models.TextField(verbose_name="Qisqa ta'rif")
    full_description = models.TextField(verbose_name="To'liq ta'rif", blank=True)

    price_from = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx (dan)", null=True, blank=True)
    price_to = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx (gacha)", null=True, blank=True)
    duration = models.IntegerField(verbose_name="Davomiyligi (daqiqa)", null=True, blank=True)

    image = models.ImageField(upload_to="services/", verbose_name="Rasm", null=True, blank=True)

    is_popular = models.BooleanField(default=False, verbose_name="Mashhur")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    order = models.IntegerField(default=0, verbose_name="Tartib")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan")

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_popular']),
            models.Index(fields=['department', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})

    def get_price_display(self):
        """Narx formati"""
        if self.price_from and self.price_to:
            return f"{self.price_from:,.0f} - {self.price_to:,.0f} so'm"
        elif self.price_from:
            return f"{self.price_from:,.0f} so'm dan"
        return "Narx individual"

    def get_duration_display(self):
        """Vaqt formati"""
        if self.duration:
            return f"{self.duration} daqiqa"
        return "Vaqt individual"


class Doctor(models.Model):
    """Shifokorlar ma'lumotlari"""
    GENDER_CHOICES = [
        ('M', 'Erkak'),
        ('F', 'Ayol'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile",null=True, blank=True, verbose_name="Foydalanuvchi")

    first_name = models.CharField(max_length=200, verbose_name="Ism")
    last_name = models.CharField(max_length=200, verbose_name="Familiyasi")
    middle_name = models.CharField(max_length=200, verbose_name="Otasining ismi", null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL Slug")
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, verbose_name="Jinsi")
    photo = models.ImageField(upload_to="doctors/", verbose_name="Rasm")

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="doctors", verbose_name="Bo'lim")
    specialization = models.CharField(max_length=200, verbose_name="Mutaxassislik")
    degree = models.CharField(max_length=200, verbose_name="Ilmiy daraja", blank=True)
    experience_years = models.IntegerField(verbose_name="Tajriba yili", validators=[MinValueValidator(0)])
    bio = models.TextField(verbose_name="Biografiya")
    education = models.TextField(verbose_name="Education", blank=True)
    achievements = models.TextField(verbose_name="Yutuqlar", blank=True)

    import datetime

    work_start = models.TimeField(default=datetime.time(9, 0), verbose_name="Ish boshlash vaqti")
    work_end = models.TimeField(default=datetime.time(18, 0), verbose_name="Ish tugash vaqti")

    consultation_duration = models.IntegerField(default=30, verbose_name="Konsultatsiya davomiyligi (daqiqa)")

    is_mon = models.BooleanField(default=True, verbose_name="Dushanba")
    is_tue = models.BooleanField(default=True, verbose_name="Seshanba")
    is_wed = models.BooleanField(default=True, verbose_name="Chorshanba")
    is_thu = models.BooleanField(default=True, verbose_name="Payshanba")
    is_fri = models.BooleanField(default=True, verbose_name="Juma")
    is_sat = models.BooleanField(default=False, verbose_name="Shanba")
    is_sun = models.BooleanField(default=False, verbose_name="Yakshanba")

    phone = models.CharField(max_length=13, verbose_name="Telefon",
                             validators=[RegexValidator(regex=r'^\+?998\d{9}$', message="Telefon +998XXXXXXXXX formatida bo'lishi kerak")])

    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name="Reying", validators=[MinValueValidator(0), MaxValueValidator(5)])
    patients_count =models.IntegerField(default=0, verbose_name="Bemorlar soni")

    is_available = models.BooleanField(default=True, verbose_name="Mavjud")
    is_futured = models.BooleanField(default=False, verbose_name="Asosiy sahifada")
    order = models.IntegerField(default=0, verbose_name="Tartib raqami")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    class Meta:
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"
        ordering = ['order', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_available', 'is_futured']),
            models.Index(fields=['department', 'is_available']),
        ]

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}")
        super().save(*args, **kwargs)

    def get_full_name(self):
        """To'liq ismi"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def get_working_days(self):
        """Ish kunlari ro'yxati"""
        days =[]
        day_map = {
            'is_mon': 'Dushanba',
            'is_tue': 'Seshanba',
            'is_wed': 'Chorshanba',
            'is_thu': 'Payshanba',
            'is_fri': 'Juma',
            'is_sat': 'Shanba',
            'is_sun': 'Yakshanba',
        }
        for field, name in day_map.items():
            if getattr(self, field):
                days.append(name)
        return ', '.join(days) if days else 'Ish kunlari belgilanmagan'

    def get_working_hours(self):
        """Ish soatlari"""
        return f"{self.work_start.strftime('%H:%M')} - {self.work_end.strftime('%H:%M')}"


class ContactMessage(models.Model):
    """Bog'lanish xabarlari"""
    name = models.CharField(max_length=120, verbose_name="Ism")
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    phone = models.CharField(max_length=120, verbose_name="Telefon")
    subject = models.CharField(max_length=120, verbose_name="Mavzu")
    message = models.TextField(verbose_name="Xabar")
    is_read = models.BooleanField(default=False, verbose_name="O'qilgan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan")

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class SiteSettings(models.Model):
    """Sayt uchun global sozlamalar (singleton)"""
    clinic_name = models.CharField(max_length=200, verbose_name="Klinika nomi", default="MediNest")
    phone_primary = models.CharField(max_length=20, verbose_name="Asosiy telefon", default="+998 90 123 45 67")
    phone_emergency = models.CharField(max_length=20, verbose_name="Tez yordam telefoni", default="+998 90 123 45 67")
    email = models.EmailField(verbose_name="Email", default="info@medinest.uz")
    address = models.CharField(max_length=300, verbose_name="Manzil", default="Toshkent shahar, Chilonzor tumani")
    
    working_hours_weekday = models.CharField(max_length=100, verbose_name="Hafta ish kunlari", default="Dush-Juma: 09:00 - 18:00")
    working_hours_weekend = models.CharField(max_length=100, verbose_name="Dam olish kunlari", default="Shanba: 09:00 - 14:00")
    
    patients_count = models.IntegerField(default=25000, verbose_name="Davolangan bemorlar soni")
    years_experience = models.IntegerField(default=15, verbose_name="Yillik tajriba")
    
    # Social media
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    telegram_url = models.URLField(blank=True, verbose_name="Telegram")
    
    # About Us sahifasi uchun
    about_title = models.CharField(max_length=200, verbose_name="Biz haqimizda - Sarlavha", 
                                   default="1985-yildan beri sog'liqni saqlashda mukammallik")
    about_intro = models.TextField(verbose_name="Biz haqimizda - Kirish matni",
                                   default="Biz ajoyib tibbiy yordam tushunishdan boshlanadi deb ishonadi. Bizning professional jamoamiz zamonaviy texnologiyalarni g'amxo'rlik bilan birlashtiradi.")
    about_trusted_title = models.CharField(max_length=200, verbose_name="Ishonchli sog'liqni saqlash - Sarlavha",
                                           default="Ishonchli sog'liqni saqlash provayderi")
    about_trusted_description = models.TextField(verbose_name="Ishonchli sog'liqni saqlash - Tavsif",
                                                 default="Bizning klinikamiz eng yuqori sifatli tibbiy xizmatlarni taqdim etishga ixtisoslashgan.")
    
    mission_text = models.TextField(verbose_name="Missiya matni",
                                    default="Har bir shaxsning o'ziga xos ehtiyojlariga moslashtirilgan shaxsiylashtirilgan parvarishni ta'minlash, tibbiy mukammallikni haqiqiy g'amxo'rlik bilan birlashtirgan keng qamrovli, bemor-markazli sog'liqni saqlash xizmatlarini taqdim etish.")
    vision_text = models.TextField(verbose_name="Viziya matni",
                                   default="Mintaqamizda innovatsion davolanish, ajoyib natijalar va jamiyatimiz hayotini yaxshilashga sodiqligimiz bilan tan olingan yetakchi sog'liqni saqlash provayderi bo'lish.")
    promise_text = models.TextField(verbose_name="Va'da matni",
                                    default="Har bir bemor qulay, qo'llab-quvvatlovchi muhitda eng yuqori sifatli parvarishni oladi, bu yerda ularning sog'lig'i, qadr-qimmati va farovonligi bizning asosiy ustuvorliklarimizdir.")
    
    # Images
    about_main_image = models.ImageField(upload_to='site_settings/', verbose_name="Biz haqimizda - Asosiy rasm", null=True, blank=True)
    about_image_2 = models.ImageField(upload_to='site_settings/', verbose_name="Biz haqimizda - Kichik rasm 1", null=True, blank=True)
    about_image_3 = models.ImageField(upload_to='site_settings/', verbose_name="Biz haqimizda - Kichik rasm 2", null=True, blank=True)
    
    class Meta:
        verbose_name = "Sayt sozlamalari"
        verbose_name_plural = "Sayt sozlamalari"
    
    def __str__(self):
        return self.clinic_name
    
    def save(self, *args, **kwargs):
        # Singleton pattern - faqat bitta yozuv bo'lishi mumkin
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Sozlamalarni olish yoki yaratish"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class ServiceFeature(models.Model):
    """Xizmatning o'ziga xos xususiyatlari"""
    service = models.ForeignKey(Service, related_name='features', on_delete=models.CASCADE, verbose_name="Xizmat")
    text = models.CharField(max_length=200, verbose_name="Xususiyat matni")
    icon = models.CharField(max_length=50, verbose_name="Icon class", default="bi bi-check-circle")
    order = models.IntegerField(default=0, verbose_name="Tartib")
    
    class Meta:
        verbose_name = "Xizmat xususiyati"
        verbose_name_plural = "Xizmat xususiyatlari"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.service.name} - {self.text}"


class AboutStatistic(models.Model):
    """Biz haqimizda sahifasi uchun statistikalar"""
    value = models.IntegerField(verbose_name="Qiymat (raqam)")
    suffix = models.CharField(max_length=10, verbose_name="Qo'shimcha (%, + va h.k.)", blank=True, default="")
    title = models.CharField(max_length=100, verbose_name="Sarlavha")
    description = models.CharField(max_length=200, verbose_name="Qisqa tavsif")
    order = models.IntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        verbose_name = "Biz haqimizda - Statistika"
        verbose_name_plural = "Biz haqimizda - Statistikalar"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.value}{self.suffix} - {self.title}"
