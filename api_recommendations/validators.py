from rest_framework.exceptions import ValidationError

STOP_WORDS = ['казино', 'криптовалюта', 'крипта', 'биржа', 'дешево', 'бесплатно', 'обман', 'полиция', 'радар',
              'реклама', 'ставки', 'кредит', 'займ', 'долг', 'алкоголь', 'наркотики', 'порнография']


class StopWordsValidator:
    """Класс валидатора, проверяющего входящий контент на наличие плохих слов"""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        field_content = dict(value).get(self.field)

        if field_content is not None:
            for stop_word in STOP_WORDS:
                if stop_word in field_content.lower() or field_content.lower() in stop_word:
                    raise ValidationError(f'Слово "{stop_word}" недопустимо!')
