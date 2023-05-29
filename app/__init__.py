from flask import Flask, render_template, redirect, url_for


app = Flask(__name__)
app.config.from_object('config.Config')


from . import views


if __name__ == '__main__':
    app.run()