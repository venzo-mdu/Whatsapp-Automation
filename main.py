from core import create_app,scheduler
from core.views import views

app = create_app()
app.debug = True
app.register_blueprint(views,url_prefix='')


if __name__ == "__main__":
    app.run

