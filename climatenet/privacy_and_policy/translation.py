# translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import PrivacyPolicy

class PrivacyPolicyTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

translator.register(PrivacyPolicy, PrivacyPolicyTranslationOptions)