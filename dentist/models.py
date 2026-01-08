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

