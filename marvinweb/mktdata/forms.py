from functools import partial

from django import forms

DateInput = partial(forms.DateInput, {'class': 'datepicker'})
DATA_TIME_FRAME = [
    ("Tick", "Tick"),
    ("1Sec", "1Sec"),
    ("3Sec", "3Sec"),
    ("10Sec", "10Sec"),
    ("1Min", "1Min"),
    ("5Min", "5Min"),
    ("10Min", "10Min"),
    ("15Min", "15Min"),
    ("30Min", "30Min"),
    ("1H", "1H"),
]


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())
    show_volume = forms.BooleanField(required=False)
    time_frame = forms.ChoiceField(choices=DATA_TIME_FRAME,
                                   required=False,
                                   label='',
                                   widget=forms.Select({'class': 'select_style',
                                                        'id': 'data_bucket'
                                                        }),
                                   )
