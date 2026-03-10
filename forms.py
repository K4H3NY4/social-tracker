from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL

# ================= POST FORMS =================

class PostForm(FlaskForm):
    """Form for creating/editing posts"""
    code = StringField('Post Code', validators=[DataRequired(), Length(max=50)])
    caption = TextAreaField('Caption', validators=[Optional(), Length(max=5000)])
    taken_at = StringField('Date (YYYY-MM-DD HH:MM:SS)', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Post')

# ================= CLIENT FORMS =================

class ClientForm(FlaskForm):
    """Form for creating/editing clients"""
    name = StringField('Client Name', validators=[DataRequired(), Length(max=200)])
    instagram = StringField('Instagram Handle', validators=[Optional(), Length(max=100)])
    facebook = StringField('Facebook Page', validators=[Optional(), Length(max=100)])
    tiktok = StringField('TikTok Handle', validators=[Optional(), Length(max=100)])
    contract = StringField('Contract URL', validators=[Optional(), URL()])
    submit = SubmitField('Save Client')