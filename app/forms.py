from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import Optional

def_val = """{
    Getspecializations{
         edges {
             node { id, name } 
            } 
        } 
    } """
class QueryForm(FlaskForm):
    query = TextAreaField('Query', validators=[Optional()], default=def_val)
    submit = SubmitField('Send')