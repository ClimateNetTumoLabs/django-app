from modeltranslation.translator import translator, TranslationOptions
from .models import Participant


class ParticipantTranslationOptions(TranslationOptions):
    fields = ('name', 'job')  # Fields to be translated


translator.register(Participant, ParticipantTranslationOptions)
