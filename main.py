from flask import Flask, render_template, request, session, redirect, send_file, url_for
from flask_mail import Mail, Message
import numpy as np
import os
from model import *
from updatedatabase import *

app = Flask(__name__)
app.secret_key = "abcd"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ankushmulewar51@gmail.com'
app.config['MAIL_PASSWORD'] = 'nllmgnqszxwombvp'
app.config['MAIL_USE_TSL'] = False
app.config['MAIL_USE_SSL'] = True

mymail = Mail(app)


@app.route('/')
def index():
    try:
        alert = request.args.get('alert')
    except:
        alert = ''

    return render_template('index.html',alert=alert)


@app.route('/otpform')
def otpform():
    try:
        alert = request.args.get('alert')
    except:
        alert = ''
    return render_template('otpform.html',alert=alert)


@app.route('/otpconfirmation', methods=['GET', 'POST'])
def otpconfirmtion():
    if request.method == 'POST':

        # session returns int while form returns str so type casting is used
        if str(session['otp']) == str(request.form['otp']):
            return redirect('/signup')
        else:
            return redirect(url_for('otpform',alert=1))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        # msg = ""
        if request.form['passw'] == request.form['cpassw']:
            name = request.form['name']
            email = request.form['email']
            passw = request.form['passw']

            db = Database()

            # returns status as False and msg if account alredy exist
            status = db.checkaccountexist(email)
            if status:
                return redirect(url_for('index', alert=3))

            session['name'] = name
            session['email'] = email
            session['passw'] = passw

            otp = np.random.randint(100000, 999999)
            session['otp'] = otp

            msg = Message('RitCloud Account Management', sender='ankushmulewr51@gmail.com', recipients=[email])
            msg.body = '**OTP(One Time Password) for account - ' + str(
                otp) + '**\n\nEnter this OTP and proceed signup.\n\nNote:\n1. This OTP is valid for 24hrs only. \n2. Do not reply this mail.'
            mymail.send(msg)

            return redirect('/otpform')

    else:
        email = session['email']
        name = session['name']
        passw = session['passw']

        db = Database()

        # returns status if account does not exist
        status = db.setdata(name, email, passw)

        os.mkdir('uploads/' + email)
        if status:
            msg = Message("RitCloud Account Management", sender="ankushmulewar51@gmail.com", recipients=[email])
            msg.body = 'Account Created Successfully...!\nYou can now log in to RitCloud'
            mymail.send(msg)
        else:
            return redirect(url_for('index', alert=6))

        return redirect(url_for('index', alert=2))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        passw = request.form['passw']

        db = Database()
        status, name = db.checklogin(email, passw)
        if status:
            session['email'] = email
            session['name'] = name
            return redirect('/home')

        else:
            return redirect(url_for('index',alert=7))


@app.route('/home')
def home():
    return render_template('home.html',alert='1')


@app.route('/upload')
def upload():
    try:
        alert = request.args.get('alert')
    except:
        alert = ''
    return render_template('upload.html',alert=alert)


@app.route('/uploadhandle', methods=['GET', 'POST'])
def uploadhandle():
    if request.method == 'POST':
        files = request.files['ufile']
        files.save('uploads/' + session['email'] + "/" + files.filename)
        return redirect(url_for('upload',alert=1))


@app.route('/download')
def download():
    try:
        alert = request.args.get('alert')
    except:
        alert = ''

    filels = os.listdir('uploads/' + session['email'])

    return render_template('download.html', fileslist=filels, alert=alert)


@app.route('/downloadfile', methods=['GET', 'POST'])
def downloadfile():
    if request.method == "POST":
        fname = request.form['file']
        path = 'uploads/' + session['email'] + '/' + str(fname)
        return send_file(path, as_attachment=True)


@app.route('/deletefile', methods=['GET', 'POST'])
def deletefile():
    if request.method == "POST":
        file = request.form['filename']
        os.remove('uploads/' + session['email'] + '/' + file)

    return redirect(url_for('download',alert=1))


@app.route('/rename', methods=['GET', 'POST'])
def rename():
    if request.method == 'POST':
        oldname = 'uploads' + '/' + session['email'] + '/' + request.form['oldname']
        newname = 'uploads' + '/' + session['email'] + '/' + request.form['newname']
        os.rename(oldname, newname)
    return redirect(url_for('download',alert=2))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        del session['name']
        del session['email']
    return redirect(url_for('index', alert=1))


@app.route('/forgotpassword')
def forgotpassword():
    try:
        alert = request.args.get('alert')
    except:
        alert = ''

    return render_template('forgotpassword.html',alert=alert)


@app.route('/forgotpasswordhandle', methods=['GET', 'POST'])
def forgotpasswordhandle():
    if request.method == 'POST':
        email = request.form['email']
        session['email'] = email
        db = Database()
        status = db.checkaccountexist(email)

        if status == False:
            # send msgf or unsuccessfull
            return redirect(url_for('forgotpassword',alert="1"))

        else:
            msg = Message('RitCloud Account Management', sender='ankushmulewar51@gmail.com', recipients=[email])
            otp = np.random.randint(100000, 999999)
            session['otp'] = otp
            msg.body = 'Your OTP to Reset Password is ' + str(
                otp) + '\n\nNote:\nEnter this Otp And Proceed For Reset Password'
            mymail.send(msg)
            return redirect('/otpforgotpassword')


@app.route('/otpforgotpassword')
def otpforgotpassword():
    try:
        alert = request.args.get('alert')
    except:
        alert = ''

    return render_template('otpforgotpassword.html',alert=alert)


@app.route('/otpforgotpasswordhandle', methods=['GET', 'POST'])
def otpforgotpasswordhandle():
    if request.method == 'POST':
        otp = request.form['otp']
        if str(session['otp']) == otp:
            del session['otp']
            return redirect(url_for('resetpassword'))
        else:
            return redirect(url_for('otpforgotpassword',alert='1'))


@app.route('/resetpassword')
def resetpassword():
    try:
        alert = request.args.get('alert')
    except:
        alert = ''

    return render_template('resetpassword.html',alert=alert)


@app.route('/resetpasswordhandle', methods=['GET', 'POST'])
def resetpasswordhandle():
    if request.method == 'POST':
        if request.form['passw'] == request.form['cpassw']:
            passw = request.form['cpassw']
            db = UpdateDatabase()
            status = db.updatepass(passw, session['email'])

            del session['email']

            if status:
                return redirect(url_for('index', alert=4))
        else:
            return redirect(url_for('resetpassword',alert=1))


if __name__ == '__main__':
    app.run(debug=True)
