from datetime import date, timedelta, timezone
from calendar import monthrange
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .models import Day, TimeBlock, Quote, EveningReflection, UserProfile
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .forms import RegisterForm, EmailAuthenticationForm
from django.utils import timezone



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .forms import RegisterForm
from .models import UserProfile


# ===================================================
# 🔐 REGISTER
# ===================================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect("today")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = request.build_absolute_uri(
            reverse("activate", args=[uidb64, token])
        )

        text_message = render_to_string(
            "planner/email/confirm_email.txt",
            {
                "user": user,
                "activation_link": activation_link,
            }
        )

        html_message = render_to_string(
            "planner/email/confirm_email.html",
            {
                "user": user,
                "activation_link": activation_link,
            }
        )

        email = EmailMultiAlternatives(
            subject="🌸 Confirmă contul tău",
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        return render(request, "planner/auth/check_email.html")

    return render(request, "planner/auth/register.html", {"form": form})


# ===================================================
# ✅ ACTIVATE ACCOUNT
# ===================================================
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        UserProfile.objects.get_or_create(user=user)

        return render(request, "planner/auth/email_confirm_success.html")

    return render(request, "planner/auth/email_confirm_invalid.html")


# ===================================================
# 🔑 LOGIN
# ===================================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("today")

    form = EmailAuthenticationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("today")

    return render(request, "planner/auth/login.html", {"form": form})


# ===================================================
# 🚪 LOGOUT
# ===================================================
def logout_view(request):
    logout(request)
    return redirect("home")



from .forms import ProfileForm

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    saved = False
    if request.method == "POST":
        profile.nickname = request.POST.get("nickname")
        profile.bio = request.POST.get("bio")
        profile.save()
        saved = True

    return render(request, "planner/auth/profile.html", {
        "profile": profile,
        "saved": saved
    })


# ===================================================
# 🌱 LOGICĂ EMOȚIONALĂ
# ===================================================

MOOD_LIMITS = {
    "very_bad": 1,
    "bad": 3,
    "neutral": 5,
    "good": 7,
    "very_good": 99,
}


def is_gentle_day(day):
    yesterday = day.date - timedelta(days=1)
    yd = Day.objects.filter(user=day.user, date=yesterday).first()
    return bool(yd and yd.mood in ["bad", "very_bad"])


def should_force_rest(day):
    last_days = Day.objects.filter(
        user=day.user,
        date__lt=day.date
    ).order_by("-date")[:3]
    return sum(d.mood in ["bad", "very_bad"] for d in last_days) >= 2


def max_tasks_for_day(day):
    if day.rest_day:
        return 1
    return MOOD_LIMITS.get(day.mood, 5)


# ===================================================
# 🏠 HOME
# ===================================================

def home_view(request):
    if request.user.is_authenticated:
        return redirect("today")

    quote = Quote.objects.filter(active=True).order_by("?").first()

    return render(request, "planner/home.html", {
        "quote": quote,
        "today": date.today(),
    })


# ===================================================
# 📅 DAY
# ===================================================

@login_required
def today_view(request):
    today = date.today()
    day, _ = Day.objects.get_or_create(user=request.user, date=today)

    if should_force_rest(day):
        day.rest_day = True
        day.save()

    message = None
    if day.rest_day:
        message = "🌱 Azi e o zi de refacere. Un singur lucru mic e suficient."
    elif is_gentle_day(day):
        message = "🌿 Azi fii blândă cu tine."

    quote = Quote.objects.filter(
        Q(mood=day.mood) | Q(mood__isnull=True),
        active=True
    ).order_by("?").first()

    return render(request, "planner/day.html", {
        "day": day,
        "time_blocks": day.time_blocks.all(),
        "limit": max_tasks_for_day(day),
        "message": message,
        "quote": quote,
    })


from datetime import date as date_cls
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Day



@login_required
def day_detail_view(request, year, month, day):
    selected_date = date_cls(year, month, day)

    day_obj, created = Day.objects.get_or_create(
        user=request.user,
        date=selected_date
    )

    message = None
    if created:
        if selected_date == date_cls.today():
            message = "Aceasta este azi. Fără presiune. 🌿"
        elif selected_date < date_cls.today():
            message = "Zi din trecut. Poți reflecta în ritmul tău. 🤍"
        else:
            message = "Zi din viitor. Nu trebuie încă să fie clară. ✨"

    reflection = EveningReflection.objects.filter(day=day_obj).first()

    return render(request, "planner/day.html", {
        "day": day_obj,
        "time_blocks": day_obj.time_blocks.order_by("start_time"),
        "limit": max_tasks_for_day(day_obj),
        "message": message,
        "reflection": reflection,

        # ✅ ASTA LIPSEA
        "quote": day_obj.closing_quote,
    })





# ===================================================
# 🗓 CALENDAR
# ===================================================

@login_required
def calendar_view(request):
    today = date.today()
    days = []

    for d in range(1, monthrange(today.year, today.month)[1] + 1):
        current = date(today.year, today.month, d)
        day_obj = Day.objects.filter(user=request.user, date=current).first()
        days.append({"date": current, "day": day_obj})

    return render(request, "planner/calendar.html", {
        "year": today.year,
        "month": today.month,
        "days": days,
    })


# ===================================================
# ⏰ TIMEBLOCKS
# ===================================================

@login_required
def add_timeblock(request):
    if request.method == "POST":
        day = get_object_or_404(
            Day,
            id=request.POST.get("day_id"),
            user=request.user
        )

        if day.time_blocks.count() < max_tasks_for_day(day):
            TimeBlock.objects.create(
                day=day,
                title=request.POST.get("title"),
                start_time=request.POST.get("start_time"),
                end_time=request.POST.get("end_time"),
            )

    return redirect(
        "day_detail",
        year=day.date.year,
        month=day.date.month,
        day=day.date.day
    )


@login_required
def toggle_timeblock(request, block_id):
    block = get_object_or_404(
        TimeBlock,
        id=block_id,
        day__user=request.user
    )

    block.completed = not block.completed
    block.save(update_fields=["completed"])

    day = block.day

    # ✅ rămâi pe ACEEAȘI zi
    return redirect(
        "day_detail",
        year=day.date.year,
        month=day.date.month,
        day=day.date.day
    )


# ===================================================
# 🎨 + 💭 ZI
# ===================================================

@login_required
def set_day_color(request):
    if request.method == "POST":
        day = get_object_or_404(
            Day,
            id=request.POST.get("day_id"),
            user=request.user
        )

        if not day.is_closed:
            day.color = request.POST.get("color")
            day.save(update_fields=["color"])

        return redirect(
            "day_detail",
            year=day.date.year,
            month=day.date.month,
            day=day.date.day
        )


@login_required
def set_day_mood(request):
    if request.method == "POST":
        day = get_object_or_404(
            Day,
            id=request.POST.get("day_id"),
            user=request.user
        )

        if not day.is_closed:
            day.mood = request.POST.get("mood")
            day.save(update_fields=["mood"])

        return redirect(
            "day_detail",
            year=day.date.year,
            month=day.date.month,
            day=day.date.day
        )
@login_required
def delete_timeblock(request, block_id):
    block = get_object_or_404(
        TimeBlock,
        id=block_id,
        day__user=request.user
    )

    day = block.day   # ✅ FOARTE IMPORTANT
    block.delete()

    return redirect(
        "day_detail",
        year=day.date.year,
        month=day.date.month,
        day=day.date.day
    )


@login_required
def update_day_text(request):
    if request.method == "POST":
        day = get_object_or_404(
            Day,
            id=request.POST.get("day_id"),
            user=request.user
        )

        if not day.is_closed:
            day.notes = request.POST.get("notes")
            day.save(update_fields=["notes"])

        return redirect(
            "day_detail",
            year=day.date.year,
            month=day.date.month,
            day=day.date.day
        )


# ===================================================
# 🌙 EVENING REFLECTION
# ===================================================
from django.utils import timezone
from random import choice

@login_required
def evening_reflection_view(request, year, month, day):
    selected_date = date_cls(year, month, day)

    day_obj = get_object_or_404(
        Day,
        user=request.user,
        date=selected_date
    )

    reflection, _ = EveningReflection.objects.get_or_create(day=day_obj)

    if request.method == "POST":
        reflection.drain = request.POST.get("drain")
        reflection.small_win = request.POST.get("small_win")
        reflection.save()

        # ✅ alegem citatul DOAR O DATĂ
        if not day_obj.closing_quote:
            quotes = Quote.objects.filter(active=True)

            # 🔹 opțional: dacă vrei după mood
            if day_obj.mood:
                mood_quotes = quotes.filter(mood=day_obj.mood)
                if mood_quotes.exists():
                    quotes = mood_quotes

            if quotes.exists():
                day_obj.closing_quote = choice(list(quotes))

        # ✅ închidem ziua
        day_obj.is_closed = True
        day_obj.closed_at = timezone.now()
        day_obj.save(update_fields=["is_closed", "closed_at", "closing_quote"])

        return redirect(
            "day_detail",
            year=year,
            month=month,
            day=day
        )

    return render(request, "planner/evening.html", {
        "day": day_obj,
        "reflection": reflection
    })




# ===================================================
# 📊 ANALYTICS
# ===================================================

@login_required
def weekly_balance_score_view(request):
    today = date.today()
    start = today - timedelta(days=6)

    days = Day.objects.filter(
        user=request.user,
        date__range=[start, today]
    )

    mood_days = sum(bool(d.mood) for d in days)
    completed_tasks = TimeBlock.objects.filter(
        day__in=days,
        completed=True
    ).count()

    score = min(
        days.count() * 10 +
        mood_days * 8 +
        completed_tasks * 2,
        100
    )

    if score < 40:
        message = "A fost o săptămână grea. Faptul că ești aici contează."
    elif score < 70:
        message = "O săptămână echilibrată, cu suișuri și coborâșuri."
    else:
        message = "Ai fost blândă cu tine săptămâna aceasta. 💗"

    return render(request, "planner/weekly_score.html", {
        "score": score,
        "message": message,
        "days_logged": days.count(),
        "completed_tasks": completed_tasks,
        "mood_days": mood_days,
    })


@login_required
def monthly_overview_view(request):
    today = date.today()
    days = Day.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    )

    return render(request, "planner/monthly_overview.html", {
        "days": days,
        "month": today.month,
        "year": today.year,
    })


@login_required
def mood_chart_view(request):
    days = Day.objects.filter(user=request.user).order_by("date")

    return render(request, "planner/chart/mood.html", {
        "days": days
    })


@login_required
def productivity_chart_view(request):
    days = Day.objects.filter(user=request.user)

    data = []
    for d in days:
        data.append({
            "date": d.date,
            "completed": d.time_blocks.filter(completed=True).count()
        })

    return render(request, "planner/chart/productivity.html", {
        "data": data
    })
