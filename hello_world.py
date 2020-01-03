from flask import Flask, render_template, flash, redirect
from forms import LoginForm
app = Flask(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

@app.route('/')
def hello_world():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/')
    return render_template('login.html', title='Sign In', form=form)

@app.route('/pollution')
def index():
    return render_template('pollution.html')

if __name__ == '__main__':
    app.run()