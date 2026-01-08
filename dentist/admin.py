from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from dentist.models import Department, Service, DepartmentFeature, WorkingHour, Doctor, ContactMessage, SiteSettings, ServiceFeature, AboutStatistic


class FeatureInline(admin.TabularInline):
    """Bo'lim xususiyatlari inline"""
    model = DepartmentFeature
    extra = 1
    verbose_name = "Xususiyat"
    verbose_name_plural = "Xususiyatlar"


class WorkingHourInline(admin.TabularInline):
    """Ish vaqtlari inline"""
    model = WorkingHour
    extra = 1
    verbose_name = "Ish vaqti"
    verbose_name_plural = "Ish vaqtlari"


class ServiceFeatureInline(admin.TabularInline):
    """Xizmat xususiyatlari inline"""
    model = ServiceFeature
    extra = 1
    verbose_name = "Xususiyat"
    verbose_name_plural = "Xususiyatlar"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Bo'limlar admin paneli"""
    list_display = ['name', 'show_icon', 'doctor_count', 'service_count', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'full_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at', 'show_image']
    date_hierarchy = 'created_at'
    inlines = [FeatureInline, WorkingHourInline]
    list_per_page = 20

    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('name', 'slug', 'icon', 'description', 'full_description')
        }),
        ('Rasm', {
            'fields': ('image', 'show_image')
        }),
        ('Holat va Tartiblash', {
            'fields': ('is_active', 'order'),
            'classes': ('wide',)
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def show_icon(self, obj):
        """Icon ko'rsatish"""
        return format_html(
            '<i class="{}" style="font-size: 24px; color: #007bff;"></i>',
            obj.icon
        )
    show_icon.short_description = 'Icon'

    def show_image(self, obj):
        """Rasmni ko'rsatish"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.image.url
            )
        return "Rasm yuklanmagan"
    show_image.short_description = 'Joriy rasm'

    def doctor_count(self, obj):
        """Shifokorlar soni"""
        count = obj.doctors.filter(is_available=True).count()
        url = reverse('admin:dentist_doctor_changelist') + f'?department__id__exact={obj.id}'
        return format_html(
            '<a href="{}" style="color: green; font-weight: bold;">{} ta</a>',
            url, count
        )
    doctor_count.short_description = 'Shifokorlar'

    def service_count(self, obj):
        """Xizmatlar soni"""
        count = obj.services.filter(is_active=True).count()
        url = reverse('admin:dentist_service_changelist') + f'?department__id__exact={obj.id}'
        return format_html(
            '<a href="{}" style="color: blue; font-weight: bold;">{} ta</a>',
            url, count
        )
    service_count.short_description = 'Xizmatlar'

    actions = ['activate_departments', 'deactivate_departments']

    def activate_departments(self, request, queryset):
        """Bo'limlarni faollashtirish"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} ta bo'lim faollashtirildi.", level='success')
    activate_departments.short_description = "Tanlangan bo'limlarni faollashtirish"

    def deactivate_departments(self, request, queryset):
        """Bo'limlarni o'chirish"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} ta bo'lim o'chirildi.", level='warning')
    deactivate_departments.short_description = "Tanlangan bo'limlarni o'chirish"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Xizmatlar admin paneli"""
    list_display = ['name', 'department', 'show_icon', 'price_display', 'duration_display', 'is_popular',  'is_active',  'order', 'created_at']
    list_filter = ['department', 'is_popular', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'full_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_popular', 'is_active', 'order']
    readonly_fields = ['created_at', 'updated_at', 'show_image']
    date_hierarchy = 'created_at'
    list_per_page = 20
    inlines = [ServiceFeatureInline]

    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('name', 'slug', 'department', 'icon', 'description', 'full_description')
        }),
        ('Narx va Vaqt', {
            'fields': ('price_from', 'price_to', 'duration'),
            'classes': ('wide',)
        }),
        ('Rasm', {
            'fields': ('image', 'show_image')
        }),
        ('Holat va Tartiblash', {
            'fields': ('is_popular', 'is_active', 'order'),
            'classes': ('wide',)
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def show_icon(self, obj):
        """Icon ko'rsatish"""
        return format_html(
            '<i class="{}" style="font-size: 24px; color: #28a745;"></i>',
            obj.icon
        )
    show_icon.short_description = 'Icon'

    def show_image(self, obj):
        """Rasmni ko'rsatish"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px;" />',
                obj.image.url
            )
        return "Rasm yuklanmagan"
    show_image.short_description = 'Joriy rasm'

    def price_display(self, obj):
        """Narxni formatlangan ko'rinishda (Xatolik bermaydigan variant)"""
        # 1. Avval sonlarni chiroyli matn ko'rinishiga keltiramiz (tashqarida)
        p_from_str = intcomma(int(obj.price_from)) if obj.price_from else None
        p_to_str = intcomma(int(obj.price_to)) if obj.price_to else None

        # 2. Endi format_html ichida hech qanday matematika (:,.0f) ishlatmaymiz
        # Faqat tayyor matnlarni ({}) chiqaramiz
        if p_from_str and p_to_str:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} - {} so\'m</span>',
                p_from_str, p_to_str
            )
        elif p_from_str:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} so\'m dan</span>',
                p_from_str
            )
        return format_html('<span style="color: #6c757d;">Individual</span>')

    price_display.short_description = 'Narx'

    def duration_display(self, obj):
        """Davomiylikni ko'rsatish"""
        if obj.duration:
            return format_html(
                '<span style="color: #007bff;">{} daqiqa</span>',
                obj.duration
            )
        return format_html('<span style="color: #6c757d;">Individual</span>')
    duration_display.short_description = 'Davomiyligi'

    actions = ['make_popular', 'make_not_popular', 'activate_services', 'deactivate_services']

    def make_popular(self, request, queryset):
        """Mashhur qilish"""
        updated = queryset.update(is_popular=True)
        self.message_user(request, f"{updated} ta xizmat mashhur qilindi.", level='success')
    make_popular.short_description = 'Mashhur qilish'

    def make_not_popular(self, request, queryset):
        """Mashhurlikni bekor qilish"""
        updated = queryset.update(is_popular=False)
        self.message_user(request, f"{updated} ta xizmat oddiy holatga qaytarildi.", level='info')
    make_not_popular.short_description = 'Mashhur emasligini belgilash'

    def activate_services(self, request, queryset):
        """Xizmatlarni faollashtirish"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} ta xizmat faollashtirildi.", level='success')
    activate_services.short_description = 'Faollashtirish'

    def deactivate_services(self, request, queryset):
        """Xizmatlarni o'chirish"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} ta xizmat o'chirildi.", level='warning')
    deactivate_services.short_description = 'O\'chirish'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Shifokorlar admin paneli"""
    list_display = ['show_photo', 'get_full_name', 'department', 'specialization', 'experience_years', 'rating_display', 'patients_count', 'is_available', 'is_futured', 'order']
    list_filter = ['department', 'gender', 'is_available', 'is_futured','created_at']
    search_fields = ['first_name', 'last_name', 'middle_name', 'specialization', 'bio']
    prepopulated_fields = {'slug': ('first_name', 'last_name')}
    list_editable = ['is_available', 'is_futured', 'order']
    readonly_fields = ['created_at', 'updated_at', 'show_large_photo']
    date_hierarchy = 'created_at'
    list_per_page = 20

    fieldsets = (
        ('Shaxsiy Ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'middle_name', 'slug', 'gender', 'photo', 'show_large_photo')
        }),
        ('Professional Ma\'lumotlar', {
            'fields': ('department', 'specialization', 'degree', 'experience_years', 'bio', 'education', 'achievements')
        }),
        ('Ish Vaqti', {
            'fields': ('work_start', 'work_end', 'consultation_duration'),
            'classes': ('wide',)
        }),
        ('Ish Kunlari', {
            'fields': ('is_mon', 'is_tue', 'is_wed', 'is_thu', 'is_fri', 'is_sat', 'is_sun'),
            'classes': ('wide',)
        }),
        ('Aloqa', {
            'fields': ('phone',)
        }),
        ('Statistika', {
            'fields': ('rating', 'patients_count'),
            'classes': ('wide',)
        }),
        ('Holat', {
            'fields': ('is_available', 'is_futured', 'order', 'user'),
            'classes': ('wide',)
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def show_photo(self, obj):
        """Kichik rasm"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return "❌"
    show_photo.short_description = 'Rasm'

    def show_large_photo(self, obj):
        """Katta rasm"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px; object-fit: cover;" />',
                obj.photo.url
            )
        return "Rasm yuklanmagan"
    show_large_photo.short_description = 'Joriy rasm'

    def rating_display(self, obj):
        """Reytingni yulduzlar bilan"""
        stars = '⭐' * int(obj.rating)
        return format_html(
            '<span style="font-size: 16px;" title="{}/5">{}</span>',
            obj.rating, stars
        )
    rating_display.short_description = 'Reyting'

    actions = ['make_featured', 'remove_featured', 'make_available', 'make_unavailable','increment_patients']

    def make_featured(self, request, queryset):
        """Asosiy sahifaga qo'shish"""
        updated = queryset.update(is_futured=True)
        self.message_user(request, f"{updated} ta shifokor asosiy sahifaga qo'shildi.", level='success')
    make_featured.short_description = 'Asosiy sahifaga qo\'shish'

    def remove_featured(self, request, queryset):
        """Asosiy sahifadan olib tashlash"""
        updated = queryset.update(is_futured=False)
        self.message_user(request, f"{updated} ta shifokor asosiy sahifadan olib tashlandi.", level='info')
    remove_featured.short_description = 'Asosiy sahifadan olib tashlash'

    def make_available(self, request, queryset):
        """Mavjud qilish"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f"{updated} ta shifokor mavjud qilindi.", level='success')
    make_available.short_description = 'Mavjud qilish'

    def make_unavailable(self, request, queryset):
        """Mavjud emasligini belgilash"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f"{updated} ta shifokor mavjud emas holatiga o'tkazildi.", level='warning')
    make_unavailable.short_description = 'Mavjud emas qilish'

    def increment_patients(self, request, queryset):
        """Bemorlar sonini oshirish"""
        for doctor in queryset:
            doctor.patients_count += 1
            doctor.save()
        self.message_user(
            request,
            f"{queryset.count()} ta shifokorning bemorlar soni oshirildi.",
            level='success'
        )
    increment_patients.short_description = 'Bemorlar sonini +1 qilish'


# DepartmentFeature va WorkingHour uchun alohida admin (ixtiyoriy)
@admin.register(DepartmentFeature)
class DepartmentFeatureAdmin(admin.ModelAdmin):
    """Bo'lim xususiyatlari"""
    list_display = ['department', 'text']
    list_filter = ['department']
    search_fields = ['text', 'department__name']


@admin.register(WorkingHour)
class WorkingHourAdmin(admin.ModelAdmin):
    """Ish vaqtlari"""
    list_display = ['department', 'day_range', 'time_range']
    list_filter = ['department']
    search_fields = ['department__name', 'day_range']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Xabarlar admin paneli"""

    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Yuboruvchi', {
            'fields': ('name', 'email')
        }),
        ('Xabar', {
            'fields': ('subject', 'message')
        }),
        ('Holat', {
            'fields': ('is_read',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """O'qilgan deb belgilash"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} ta xabar o\'qilgan')

    mark_as_read.short_description = "O'qilgan"

    def mark_as_unread(self, request, queryset):
        """O'qilmagan deb belgilash"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} ta xabar o\'qilmagan')

    mark_as_unread.short_description = "O'qilmagan"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Sayt sozlamalari admin paneli"""
    list_display = ['clinic_name', 'phone_primary', 'email', 'patients_count']
    
    fieldsets = (
        ('Klinika Ma\'lumotlari', {
            'fields': ('clinic_name', 'address', 'email')
        }),
        ('Telefon Raqamlari', {
            'fields': ('phone_primary', 'phone_emergency')
        }),
        ('Ish Vaqti', {
            'fields': ('working_hours_weekday', 'working_hours_weekend')
        }),
        ('Statistika', {
            'fields': ('patients_count', 'years_experience')
        }),
        ('Ijtimoiy Tarmoqlar', {
            'fields': ('facebook_url', 'instagram_url', 'telegram_url'),
            'classes': ('collapse',)
        }),
        ('Biz Haqimizda Sahifasi', {
            'fields': ('about_title', 'about_intro', 'about_trusted_title', 'about_trusted_description', 'about_main_image', 'about_image_2', 'about_image_3'),
            'classes': ('collapse',)
        }),
        ('Missiya / Viziya / Va\'da', {
            'fields': ('mission_text', 'vision_text', 'promise_text'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Faqat bitta yozuv bo'lishi mumkin
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # O'chirishga ruxsat bermaslik
        return False


@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):
    """Xizmat xususiyatlari"""
    list_display = ['service', 'text', 'icon', 'order']
    list_filter = ['service']
    search_fields = ['text', 'service__name']
    list_editable = ['order']


@admin.register(AboutStatistic)
class AboutStatisticAdmin(admin.ModelAdmin):
    """Biz haqimizda statistikalari"""
    list_display = ['value', 'suffix', 'title', 'description', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']