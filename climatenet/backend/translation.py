# translation.py

from modeltranslation.translator import translator, TranslationOptions
from .models import TeamMember, Device

class TeamMemberTranslationOptions(TranslationOptions):
    fields = ('name', 'position')

translator.register(TeamMember, TeamMemberTranslationOptions)


class DeviceTranslationOptions(TranslationOptions):
    fields = ('name', 'parent_name')

translator.register(Device, DeviceTranslationOptions)