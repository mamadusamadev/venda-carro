from django import forms
from django.core.exceptions import ValidationError
from forms.widgets import MultipleImageInput


class MultipleFileField(forms.FileField):
    """Campo personalizado para múltiplos arquivos"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleImageInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Se não há dados, retorna lista vazia
        if not data:
            return []
        
        # Se data é uma lista, processa cada arquivo
        if isinstance(data, list):
            result = []
            for file in data:
                try:
                    # Usa o método clean do campo pai para cada arquivo
                    cleaned_file = super().clean(file, initial)
                    if cleaned_file:
                        result.append(cleaned_file)
                except ValidationError:
                    # Se um arquivo específico falha, continua com os outros
                    pass
            return result
        else:
            # Se é um único arquivo, retorna como lista
            cleaned_file = super().clean(data, initial)
            return [cleaned_file] if cleaned_file else []


class MultipleImageField(MultipleFileField):
    """Campo específico para múltiplas imagens com validações"""
    
    def __init__(self, *args, **kwargs):
        self.max_files = kwargs.pop('max_files', 10)
        self.max_file_size = kwargs.pop('max_file_size', 5 * 1024 * 1024)  # 5MB
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        files = super().clean(data, initial)
        
        if not files:
            return files
        
        # Verifica número máximo de arquivos
        if len(files) > self.max_files:
            raise ValidationError(f"Máximo de {self.max_files} imagens permitidas.")
        
        # Valida cada arquivo
        for file in files:
            # Verifica tamanho
            if file.size > self.max_file_size:
                raise ValidationError(f"A imagem '{file.name}' é muito grande. Máximo {self.max_file_size // (1024*1024)}MB.")
            
            # Verifica tipo
            if not file.content_type.startswith('image/'):
                raise ValidationError(f"'{file.name}' não é um arquivo de imagem válido.")
        
        return files 