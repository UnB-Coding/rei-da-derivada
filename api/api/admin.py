from django import forms
from django.contrib import admin
from django.forms import ValidationError
from .models import Token, Event, SumulaImortal, SumulaClassificatoria, PlayerScore, Player, Staff, Results
from guardian.admin import GuardedModelAdmin
from django.db.models import Count


@admin.register(Token)
class TokenAdmin(GuardedModelAdmin):
    def event(self, obj):
        return obj.event
    list_display = ['token_code', 'id', 'created_at', 'used', 'event']
    search_fields = ['token_code']
    fields = ['used']


@admin.register(Event)
class EventAdmin(GuardedModelAdmin):
    def final_results_published(self, obj):
        return obj.is_final_results_published
    final_results_published.short_description = 'Final Results Published?'
    final_results_published.boolean = True

    def imortal_results_published(self, obj):
        return obj.is_imortal_results_published
    imortal_results_published.short_description = 'Imortal Results Published?'
    imortal_results_published.boolean = True
    list_display = ['id', 'token', 'join_token', 'name', 'active',
                    'final_results_published', 'imortal_results_published']
    search_fields = ['token', 'name', 'active', 'join_token']
    fields = ['token', 'name', 'active', 'admin_email']
    ordering = ['name', 'active', 'is_final_results_published',
                'is_imortal_results_published', 'token', 'join_token']


class SumulaAdmin(GuardedModelAdmin):

    def referees(self, obj):
        referees = []
        for referee in obj.referee.all():
            referees.append(referee.__str__())
        return ', '.join(referees)

    def player_scores(self, obj):
        scores = []
        for score in obj.scores.all():
            scores.append(score.__str__())
        return ', '.join(scores)

    @admin.display(description='Players Count')
    def players_count(self, obj):
        # Ordena pelo count de scores dentro do método
        return obj.scores.order_by('id').count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(scores_count=Count('scores'))

    def rounds_count(self, obj):
        if obj.rounds is None:
            return 0
        return len(obj.rounds)

    # def pairs_count(self, obj):
    #     pairs = []
    #     for round in obj.rounds:
    #         pairs.append(str(len(round)))
    #     return ", ".join(pairs)

    player_scores.short_description = 'Player Scores'
    referees.short_description = 'Referees'
    list_display = ['name', 'event', 'referees',
                    'id', 'player_scores', 'players_count', 'active', 'rounds_count', 'rounds']
    search_fields = ['referee__username',
                     'event__name', 'name', 'player_scores_count']
    fields = ['referee', 'event', 'name',
              'active', 'description', 'rounds']
    filter_horizontal = ['referee']
    ordering = ['event', 'name']


@ admin.register(SumulaImortal)
class SumulaImortalAdmin(SumulaAdmin):
    pass


@ admin.register(SumulaClassificatoria)
class SumulaClassificatoriaAdmin(SumulaAdmin):
    pass


class PlayerScoreForm(forms.ModelForm):
    class Meta:
        model = PlayerScore
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        self.validar_sumulas(cleaned_data)
        self.validar_evento_player(cleaned_data)
        self.validar_evento_sumula(cleaned_data)
        return cleaned_data

    def validar_sumulas(self, cleaned_data):
        sumula_classificatoria = cleaned_data.get("sumula_classificatoria")
        sumula_imortal = cleaned_data.get("sumula_imortal")
        if sumula_classificatoria and sumula_imortal:
            raise ValidationError(
                "Um jogador não pode estar em duas súmulas ao mesmo tempo.")
        elif not sumula_classificatoria and not sumula_imortal:
            raise ValidationError(
                "Um jogador deve estar em pelo menos uma súmula.")

    def validar_evento_player(self, cleaned_data):
        player = cleaned_data.get("player")
        event = cleaned_data.get("event")
        if player.event != event:
            raise ValidationError(
                "O evento de Player deve ser o mesmo Evento do objeto de PlayerScore!")

    def validar_evento_sumula(self, cleaned_data):
        sumula_classificatoria = cleaned_data.get("sumula_classificatoria")
        sumula_imortal = cleaned_data.get("sumula_imortal")
        event = cleaned_data.get("event")
        if sumula_classificatoria and sumula_classificatoria.event != event:
            raise ValidationError(
                "O evento de uma Sumula deve ser o mesmo Evento do objeto de PlayerScore!")
        elif sumula_imortal and sumula_imortal.event != event:
            raise ValidationError(
                "O evento de uma Sumula deve ser o mesmo Evento do objeto de PlayerScore!")


@ admin.register(PlayerScore)
class PlayerScoreAdmin(GuardedModelAdmin):
    form = PlayerScoreForm

    list_display = ['id', 'player', 'event', 'sumula_classificatoria',
                    'sumula_imortal', 'points', 'rounds_number']
    search_fields = ['event', 'sumula_classificatoria',
                     'sumula_imortal', 'points', 'player']
    fields = ['event', 'sumula_classificatoria',
              'sumula_imortal', 'points', 'player']


@ admin.register(Player)
class PlayerAdmin(GuardedModelAdmin):
    list_display = ['id', 'user', 'full_name', 'social_name',
                    'event', 'total_score', 'registration_email', 'is_imortal', 'is_present']
    search_fields = ['user', 'total_score', 'event', 'registration_email']
    fields = ['user', 'total_score', 'event',
              'registration_email', 'full_name', 'social_name', 'is_imortal', 'is_present']

    def username(self, obj):
        return obj.username
    # Optional, to set column header in admin interface.
    username.short_description = 'username'


@ admin.register(Staff)
class StaffAdmin(GuardedModelAdmin):
    list_display = ['id', 'full_name', 'user', 'event',
                    'registration_email', 'is_manager']
    search_fields = ['full_name', 'user', 'event', 'registration_email']
    fields = ['full_name', 'user', 'event', 'registration_email', 'is_manager']

    # def username(self, obj):
    #     return obj.username
    # # Optional, to set column header in admin interface.
    # username.short_description = 'username'


@admin.register(Results)
class ResultsAdmin(GuardedModelAdmin):
    def display_top4(self, obj):
        return ', '.join([player.__str__() for player in obj.top4.all()])
    display_top4.short_description = 'Top 4'

    def display_imortals(self, obj):
        return ', '.join([player.__str__() for player in obj.imortals.all()])
    display_imortals.short_description = 'Imortals'

    list_display = ['id', 'event', 'display_top4',
                    'display_imortals', 'ambassor', 'paladin']
    search_fields = ['event', 'top4__name',
                     'imortals__name', 'ambassor', 'paladin']
    fields = ['event', 'top4', 'imortals', 'ambassor', 'paladin']
    filter_horizontal = ['top4', 'imortals']
