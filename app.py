from os import name
from flask import Flask,render_template,request
from flask.helpers import flash
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
from datetime import datetime
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash
import pickle


from flask_sqlalchemy import SQLAlchemy
model = pickle.load (open('model.pkl','rb'))
app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config["SECRET_KEY"] = "mysecretkey"
db = SQLAlchemy(app)
login_manager = LoginManager ()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
        return User.query.get(int(user_id))


class User(UserMixin,db.Model):
        id = db.Column (db.Integer,primary_key = True)
        name = db.Column (db.String(200),nullable=False)
        email = db.Column (db.String(100),nullable=False)
        password = db.Column(db.String(100),nullable=False)
        created_at = db.Column (db.DateTime,default = datetime.utcnow)

@app.route('/',methods=['POST','GET'])
def home():
        return render_template ('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
        if request.method == 'POST':
                name= request.form['name']
                email = request.form['email']
                password = request.form ['password']

                user = User.query.filter_by(email=email).first ()
                if user:
                        flash ('User already exists, login')
                        return redirect ('signup')
                else: 
                        new_user = User(name=name,email=email,password = generate_password_hash(password,method='sha256'))
                        try:
                                db.session.add(new_user)
                                db.session.commit ()
                                print (new_user)
                                return redirect('login')
                        except:
                                 return "There was an issue signing you up"
        
        else: 
                return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
                email = request.form ['email']
                password = request.form ['password']

                user = User.query.filter_by (email=email).first ()
                if not user :
                        flash ('The email is not registered, please signup')
                        return redirect ('/login')
                elif not check_password_hash (user.password,password):
                        flash ("Please enter the correct password")
                        return redirect ('/login')
                else:
                        login_user (user)
                        return redirect ('/')
        else:
                return render_template('login.html')


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def prediction():
        if request.method == 'POST':
                age = request.form['age']
                gender = request.form['gender'].lower ()
                if gender == 'female':
                        gender = 0
                else:
                        gender = 1
                print(gender)
                int_features = [[int(age),gender]]
                final_features = (int_features)
                print (final_features)
                prediction = model.predict (final_features)
                accuracy_score = model.score (final_features,prediction)
                print("Accuracy score is: ",accuracy_score * 100,"%")
                str1 = ''.join(prediction)
                print(str1)
                return render_template('predict.html',prediction_text = str1)
        else:
               return render_template('predict.html')
        
               


@app.route('/profile',methods=['GET'])
def profile():
   return render_template ('profile.html',id= current_user.id,name= current_user.name)


@app.route('/logout')
def logout():
   logout_user ()
   return redirect ('/')

@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def method_name(id):
        user = User.query.get_or_404 (id)
        if request.method == 'POST':
                user.name = request.form ['name']
                user.email = request.form ['email']
                user.password =generate_password_hash ( request.form ['password'])
                print (user.password)

                db.session.commit ()
                return redirect ('/profile')
        else:
                return render_template ('update.html',user = user)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
   user_to_delete = User.query.get_or_404 (id)
   db.session.delete (user_to_delete)
   db.session.commit ()
   return redirect('/')

if __name__ == ('__main__'):
    app.run (debug = True)