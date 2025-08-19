from django import forms
from django.forms.widgets import FileInput
from django.utils.safestring import mark_safe


class MultipleFileInput(FileInput):
    """Widget personalizado para upload de múltiplos arquivos"""
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': True})
        super().__init__(attrs)
    
    def value_from_datadict(self, data, files, name):
        """Retorna lista de arquivos em vez de um único arquivo"""
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class MultipleImageInput(MultipleFileInput):
    """Widget específico para múltiplas imagens"""
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({
            'accept': 'image/*',
            'class': 'form-control d-none'
        })
        super().__init__(attrs) 