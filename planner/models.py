from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models



# ===================================================
# 👤 PROFIL UTILIZATOR
# ===================================================

class UserProfile(models.Model):
    PRONOUN_CHOICES = [
        ("ea", "ea / ei"),
        ("el", "el / lui"),
        ("they", "they"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    nickname = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)

    pronoun = models.CharField(
        max_length=10,
        choices=PRONOUN_CHOICES,
        blank=True
    )

    evening_reminder_time = models.TimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nickname or self.user.email



# ===================================================
# 🗓 ZIUA
# ===================================================

class Quote(models.Model):
    text = models.TextField()

    # asociat unui mood (OPȚIONAL)
    mood = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.text[:60]


class Day(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="days"
    )

    date = models.DateField()

    # ✅ STARE ZI
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)

    # 🌙 Citat final (salvat la închiderea zilei)
    closing_quote = models.ForeignKey(
        Quote,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="days"
    )

    class Mood(models.TextChoices):
        VERY_BAD = 'very_bad', '😞 Foarte greu'
        BAD = 'bad', '😕 Greu'
        NEUTRAL = 'neutral', '😐 Neutru'
        GOOD = 'good', '🙂 Bine'
        VERY_GOOD = 'very_good', '😄 Foarte bine'

    class Color(models.TextChoices):
        GREEN = 'green', 'Verde'
        YELLOW = 'yellow', 'Galben'
        RED = 'red', 'Roșu'
        BLUE = 'blue', 'Albastru'
        PURPLE = 'purple', 'Mov'

    # Emoție
    mood = models.CharField(
        max_length=20,
        choices=Mood.choices,
        blank=True,
        null=True
    )

    # Energie
    color = models.CharField(
        max_length=20,
        choices=Color.choices,
        blank=True,
        null=True
    )

    # 🌱 Zi de refacere (auto)
    rest_day = models.BooleanField(default=False)

    # 📝 Note libere
    notes = models.TextField(blank=True)

    # ⭐ Focus
    focus_of_the_day = models.CharField(
        max_length=255,
        blank=True
    )

    # 🌱 Recunoștință
    gratitude = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        unique_together = ("user", "date")  # ✅ CRUCIAL

    def __str__(self):
        return f"{self.user.username} – {self.date}"


# ===================================================
# ⏰ INTERVAL ORAR
# ===================================================

class TimeBlock(models.Model):
    class Category(models.TextChoices):
        WORK = 'work', 'Muncă'
        PERSONAL = 'personal', 'Personal'
        HEALTH = 'health', 'Sănătate'
        TRAVEL = 'travel', 'Deplasare'
        REST = 'rest', 'Odihnă'
        OTHER = 'other', 'Altele'

    day = models.ForeignKey(
        Day,
        on_delete=models.CASCADE,
        related_name="time_blocks"
    )

    title = models.CharField(max_length=100)

    start_time = models.TimeField()
    end_time = models.TimeField()

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )

    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(
                "Ora de sfârșit trebuie să fie după ora de început."
            )

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.title} ({self.start_time}–{self.end_time})"


# ===================================================
# 🌙 REFLECȚIE DE SEARĂ
# ===================================================

class EveningReflection(models.Model):
    day = models.OneToOneField(
        Day,
        on_delete=models.CASCADE,
        related_name="evening_reflection"
    )

    drain = models.TextField(blank=True)
    small_win = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reflection – {self.day.user.username} – {self.day.date}"


# ===================================================
# 💬 CITAT
# ===================================================




