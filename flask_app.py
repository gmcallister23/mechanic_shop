from app import create_app
from  app.models import db

#app = create_app('DevelopmentConfig')
app = create_app('ProductionConfig')
def reset_database():
    db.drop_all()
    db.create_all()

if __name__== "__main__":
    with app.app_context():
        #reset_database() #Comment and un comment as needed
        db.create_all()

    app.run(debug=True)

