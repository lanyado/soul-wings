from wtforms import Form, StringField, SelectField

class TestimonySearchForm(Form):
    choices = [('Video', 'Video')]
    select = SelectField('Search testemonies of type:', choices=choices)
    search = StringField('')
