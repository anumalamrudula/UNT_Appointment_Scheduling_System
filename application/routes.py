from application import app, db
from flask import render_template, request, json, jsonify, Response, redirect, flash, url_for, session, Flask
from application.models import User, Professor, Appointment,  Holiday, Professorslot, Universitymail
from application.forms import LoginForm, RegisterForm, UpdateProfileForm, SlotsForm, AuthorizeMailForm, RequestResetForm, ResetPasswordForm, ProfessorForm
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

slotsList = ["8:00 AM to 8:30 AM", "8:30 AM to 9:00 AM", "9:00 AM to 9:30 AM", "9:30 AM to 10:00 AM", "10:00 AM to 10:30 AM", "10:30 AM to 11:00 AM", "11:00 AM to 11:30 AM", "11:30 AM to 12:00 PM", "12:00 PM to 12:30 PM", "12:30 PM to 1:00 PM", "1:00 PM to 1:30 PM", "1:30 PM to 2:00 PM", "2:00 PM to 2:30 PM", "2:30 PM to 3:00 PM", "3:00 PM to 3:30 PM", "3:30 PM to 4:00 PM", "4:00 PM to 4:30 PM", "4:30 PM to 5:00 PM"]
enableNotification = 0

######################################################################
# COMPONENT  - TRIGGER NOTIFICATION: SEND EMAIL
# WRITTEN BY - MRUDULA ANUMALA
# CREATED ON - OCT 30 2020
######################################################################

def triggerMail(studentName, RECP, SUBJECT, TEXT, profComment="______________________"):

    mailserver = smtplib.SMTP('smtp.office365.com',587)
    mailserver.ehlo()
    mailserver.starttls()

    # ********* Replace with the admin credentials ***********
    # Set enableNotification = 1 (Line 11) if you set the credentials (Line 27 & 59)
    mailserver.login('mailId@unt.edu', 'Password@123')

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT

    # Create the body of the message (a plain-text and an HTML version).
    text = ""
    html = """\
    <html>
    <head></head>
    <body>
        <p>Hi {studentName},<br>
        <br>{TEXT}<br>
        {profComment}<br>
        <br>
        @Team_TECHNOCRATS<br>
        Appointment Scheduling System,<br>
        University of North Texas.<br>
        </p>
        <img src="data:image/png;base64,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" alt="Simply Easy Learning"
        width="200" height="80">
    </body>
    </html>
    """.format(studentName=studentName,TEXT=TEXT,profComment=profComment)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    RECPIENTS = [RECP]
    mailserver.sendmail('mailId@unt.edu',RECPIENTS,msg.as_string())
    mailserver.quit()

######################################################################
# COMPONENT  - SEND RESET PASSWORD MAIL
# WRITTEN BY - BHARGAVI GHANTA
# CREATED ON - NOV 08 2020
######################################################################

def send_reset_email(user):

    token = user.get_reset_token()
    mailserver = smtplib.SMTP('smtp.office365.com',587)
    mailserver.ehlo()
    mailserver.starttls()

    # ********* Replace with the admin credentials ***********
    # Set the credentials (Lines 77 & 111)
    mailserver.login('mailId@unt.edu', 'Password@123')

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "RESET PASSWORD REQUEST"
    TEXT = f'''{url_for('reset_token', token=token, _external=True)}'''

    # Create the body of the message (a plain-text and an HTML version).
    text = ""
    html = """\
    <html>
    <head></head>
    <body>
        <p>Hi {studentName},<br>
        <br> To reset your password, visit the following link:
        <br>{TEXT}<br>
        If you did not make this request then simply ignore this email and no changes will be made.<br>
        <br>
        @Team_TECHNOCRATS<br>
        Appointment Scheduling System,<br>
        University of North Texas.<br>
        </p>
        <img src="data:image/png;base64,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" alt="Simply Easy Learning"
        width="200" height="80">
    </body>
    </html>
    """.format(studentName=user.first_name,TEXT=TEXT)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    RECPIENTS = [user.email]
    mailserver.sendmail('mailId@unt.edu',RECPIENTS,msg.as_string())
    mailserver.quit()


######################################################################
# COMPONENT  - USERS INDEX PAGE
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - SEP 30 2020
######################################################################

@app.route("/index")
@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html", home=True)


######################################################################
# COMPONENT  - USERS REGISTRATION
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 8 2020
######################################################################

@app.route("/register", methods=['POST','GET'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id     = User.objects.count()
        user_id     += 1
        email       = form.email.data
        password    = form.password.data
        first_name  = form.first_name.data
        last_name   = form.last_name.data
        if 'my.unt.edu' in email:
            role = "student"
        elif 'unt.edu' in email:
            role = "staff"
        else:
            flash("Invalid domain !","danger")
            return render_template("register.html", title="Please Register Here", form=form, register=True)
        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name, role=role)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!","success")
        if role == "student":
            return redirect(url_for('studenthome'))
        elif role == "staff":
            return redirect(url_for('staffhome'))
    return render_template("register.html", title="Please Register Here", form=form, register=True)


######################################################################
# COMPONENT  - USERS LOGIN
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 8 2020
######################################################################

@app.route("/")
@app.route("/login", methods=["GET","POST"])
def login():
    if session.get('username'):
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email    = form.email.data
        password = form.password.data
        user = User.objects(email=email).first()
        if not user:
            flash("Email is incorrect. Please try again.", "danger")
        else:
            user_id = user.user_id
            if user.get_password(password):
                flash(f"{user.first_name}, you are successfully logged in!", "success")
                session['user_id'] = user.user_id
                session['username'] = user.first_name
                session['role'] = user.role
                session['email'] = user.email
                if user.role=="student":
                    return redirect(url_for('studenthome',user_id=user_id))
                elif user.role=="staff":
                    if Professor.objects(MailID=session.get('email')).first():
                        return redirect(url_for('staffhome',email=email))
                    else:
                        flash("You are not listed as a Professor in the System. Get it updated with the admin !", "danger")
                        return render_template("login.html", title="Login to UNT Appointment Application", form=form, login=True )
                elif user.role=="admin":
                    return redirect(url_for('adminhome'))
            else:
                flash("Password is incorrect. Please try again.", "danger")
    return render_template("login.html", title="Login to UNT Appointment Application", form=form, login=True )


######################################################################
# COMPONENT  - RESET PASSWORD REQUEST FORM
# WRITTEN BY - BHARGAVI GHANTA
# CREATED ON - NOV 08 2020
######################################################################

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


######################################################################
# COMPONENT  - RESET PASSWORD
# WRITTEN BY - BHARGAVI GHANTA
# CREATED ON - NOV 08 2020
######################################################################

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if session.get('username'):
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if user.get_password(form.password.data):
            flash('Your old password and new password cannot be same','danger')
        else:
            password = form.password.data
            user.set_password(password)
            user.save()
            flash('Your password has been updated! You are now able to log in ', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


######################################################################
# COMPONENT  - STUDENT : APPOINTMENT REQUESTS
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 12 2020
######################################################################

@app.route("/studenthome", methods=["GET","POST"])
def studenthome(user_id=None):
    if not session.get('username'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    profs = list(User.objects.aggregate(*[
                {
                    '$lookup': {
                        'from': 'appointment',
                        'localField': 'user_id',
                        'foreignField': 'user_id',
                        'as': 'r1'
                    }
                }, {
                    '$unwind': {
                        'path': '$r1',
                        'includeArrayIndex': 'r1_id',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$sort': {
                        'r1.date': 1
                    }
                }, {
                    '$lookup': {
                        'from': 'professor',
                        'localField': 'r1.prof_id',
                        'foreignField': 'prof_id',
                        'as': 'r2'
                    }
                }, {
                    '$unwind': {
                        'path': '$r2',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$match': {
                        'user_id': user_id
                    }
                }, {
                    '$sort': {
                        'prof_id': 1
                    }
                }
            ]))


    holidays = Holiday.objects().order_by("+date").all()
    holidaylist = []
    for holiday in holidays:
        d = holiday["date"].strftime("%m/%d/%Y")
        holidaylist.append(d)
    return render_template("studenthome.html", profs=profs, holidaylist=holidaylist, home=True, login=True, today=datetime.now())


######################################################################
# COMPONENT  - PROFESSORS : UPCOMING APPOINTMENTS
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 8 2020
######################################################################

@app.route("/staffhome")
def staffhome(email=None):
    if not session.get('username'):
        return redirect(url_for('login'))
    Prof = Professor.objects(MailID=session.get('email')).first()
    prof_id = Prof.prof_id
    students = list(Professor.objects.aggregate(*[
                {
                    '$lookup': {
                        'from': 'appointment',
                        'localField': 'prof_id',
                        'foreignField': 'prof_id',
                        'as': 'r1'
                    }
                }, {
                    '$unwind': {
                        'path': '$r1',
                        'includeArrayIndex': 'r1_id',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$sort': {
                        'r1.date': 1
                    }
                }, {
                    '$match': {
                        'r1.status': 'Approved'
                    }
                },{
                    '$lookup': {
                        'from': 'user',
                        'localField': 'r1.user_id',
                        'foreignField': 'user_id',
                        'as': 'r2'
                    }
                }, {
                    '$unwind': {
                        'path': '$r2',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$match': {
                        'prof_id': prof_id
                    }
                }, {
                    '$sort': {
                        'user_id': 1
                    }
                }
    ]))
    return render_template("staffhome.html", students=students, home=True, login=True, today=datetime.now() )


#############################################################################
# COMPONENT  - MANAGE STUDENTS & PROFESSORS APPOINTMENT REQUESTS & UPDATES
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 8 2020
#############################################################################

@app.route("/schedule", methods=["GET","POST"])
def schedule():
    if not session.get('username'):
        return redirect(url_for('login'))
    if session.get('role')=="student":
        date=request.form.get('birthdaytime')
        prof_name = request.form.get('prof_name')
        prof_id = request.form.get('prof_id')
        user_id = session.get('user_id')
        rec_id = request.form.get('id')
        req = request.form.get('req')
        date_value = request.form.get('date_value')
        slot_value = request.form.get('slot_value')
        re_req = request.form.get('re_req')
        if date_value:
            dt = date_value
        if req == "cancel":
                Appointment.objects(myid=rec_id).delete()
                flash(f"Appointment with professor {prof_name} is cancelled by you!","success")
                return redirect(url_for('studenthome'))
        elif date:
            if prof_name :
                dt = datetime.strptime(date, '%Y-%m-%d').date()
                form = SlotsForm()
                profSlots = Professorslot.objects(prof_id=prof_id, date = dt).first()
                availableSlots = slotsList.copy()
                if profSlots :
                    profblocks = profSlots["slots"]
                    indexes = [profblocks.index(x) for x in profblocks if x]
                    for index in sorted(indexes, reverse=True):
                        del availableSlots[index]
                slots = Appointment.objects(prof_id=prof_id, date = dt).all()
                scheduledSlots = []
                for i in slots:
                    scheduledSlots.append(i.slot)
                form.slot.choices = [x for x in availableSlots if x not in scheduledSlots]
                if Appointment.objects(user_id=user_id,prof_id=prof_id) and req == "reschedule":
                    return render_template("timeslot.html", form=form, appointments=True, login=True, date = dt,  prof_id=prof_id, prof_name=prof_name, req = "reschedule", rec_id=rec_id)
                elif Appointment.objects(user_id=user_id,prof_id=prof_id):
                    todaydate=datetime.now().date()
                    PrevAppointment = Appointment.objects(user_id=user_id,prof_id=prof_id).order_by("-date").first()
                    if (todaydate < PrevAppointment["date"]) :
                        flash(f"You have already requested for appointment with {prof_name}!", "danger")
                        return redirect(url_for('studenthome'))
                    else:
                        return render_template("timeslot.html", form=form, appointments=True, login=True, date = dt,  prof_id=prof_id, prof_name=prof_name)
                else:
                    return render_template("timeslot.html", form=form, appointments=True, login=True, date = dt,  prof_id=prof_id, prof_name=prof_name)
            else:
                return redirect(url_for('studenthome'))
        else:
            if Appointment.objects(user_id=user_id, date=dt, slot=slot_value, status="Requested"):
                    flash(f"You have an appointment request for that time!", "danger")
                    return redirect(url_for('studenthome'))
            if Appointment.objects(user_id=user_id, date=dt, slot=slot_value, status="Approved"):
                    flash(f"You have a scheduled appointment in that time!", "danger")
                    return redirect(url_for('studenthome'))
            else:
                if re_req == "reschedule":
                    Appointment.objects(myid=rec_id).delete()
                    flash(f"You have successfully rescheduled your appointment with {prof_name} !","success")
                else:
                    flash(f"You have successfully scheduled an appointment with {prof_name} !","success")
                if Appointment.objects.count() == 0:
                    myid = 1
                else:
                    myid = Appointment.objects().order_by('-myid').limit(-1).first().myid + 1
                Appointment(myid=myid, prof_id=prof_id, user_id=user_id, prof_name=prof_name, status="Requested", date=dt, slot=slot_value).save()
                return redirect(url_for('studenthome'))

    if session.get('role')=="staff":
        student_name = request.form.get('student_name')
        student_mail = request.form.get('student_mail')
        rec_id = request.form.get('id')
        req = request.form.get('req')
        profComment = request.form.get('comment')
        if req == "approve":
            Appointment.objects(myid=rec_id).update(status="Approved")
            flash(f"Appointment with {student_name} is approved successfully by you!","success")
            prof_name = Appointment.objects(myid=rec_id).first().prof_name
            slot = Appointment.objects(myid=rec_id).first().slot
            date = Appointment.objects(myid=rec_id).first().date
            if enableNotification==1:
                triggerMail(student_name, student_mail,"Appointment Scheduled !!",f"Your appointment on {date} at {slot} with Professor {prof_name} is approved !")
            return redirect(url_for('staffhome'))
        if req == "cancel":
            prof_name = Appointment.objects(myid=rec_id).first().prof_name
            Appointment.objects(myid=rec_id).delete()
            if profComment :
                flash(f"You have commented : {profComment}","success")
            flash(f"Appointment request from {student_name} is cancelled by you!","success")
            if enableNotification==1:
                triggerMail(student_name, student_mail,"Appointment Request Cancelled !!",f"Your appointment with Professor {prof_name} is cancelled !",profComment)
            return redirect(url_for('staffhome'))


#####################################################################################
# COMPONENT  - STUDENTS : SCHEDULE APPOINTMENT , PROFESSORS : APPOINTMENT REQUESTS
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 8 2020
#####################################################################################

@app.route("/appointments", methods=["GET","POST"])
def appointments():
    if not session.get('username'):
        return redirect(url_for('login'))
    if session.get('role')=="student":
        user_id = session.get('user_id')
        ProfData = Professor.objects.order_by("+prof_id")
        holidays = Holiday.objects().order_by("+date").all()
        holidaylist = []
        for holiday in holidays:
            d = holiday["date"].strftime("%m/%d/%Y")
            holidaylist.append(d)
        return render_template("studentsappointments.html", ProfData=ProfData, holidaylist=holidaylist, user_id=user_id, appointments=True, login=True )

    else:
        Prof = Professor.objects(MailID=session.get('email')).first()
        prof_id = Prof.prof_id
        maxDateRequest = Appointment.objects(prof_id=prof_id,status="Requested").order_by("-date").first()
        students = list(Professor.objects.aggregate(*[
                {
                    '$lookup': {
                        'from': 'appointment',
                        'localField': 'prof_id',
                        'foreignField': 'prof_id',
                        'as': 'r1'
                    }
                }, {
                    '$unwind': {
                        'path': '$r1',
                        'includeArrayIndex': 'r1_id',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$sort': {
                        'r1.date': 1
                    }
                }, {
                    '$match': {
                        'r1.status': 'Requested'
                    }
                },{
                    '$lookup': {
                        'from': 'user',
                        'localField': 'r1.user_id',
                        'foreignField': 'user_id',
                        'as': 'r2'
                    }
                }, {
                    '$unwind': {
                        'path': '$r2',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$match': {
                        'prof_id': prof_id
                    }
                }, {
                    '$sort': {
                        'user_id': 1
                    }
                }
            ]))
        return render_template("staffappointments.html", appointments=True, students=students, title="Appointments", today=datetime.now(), maxDate=maxDateRequest, todayDate=(datetime.now()).date())


######################################################################
# COMPONENT  - PROFESSORS : MANAGE SLOTS
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 26 2020
######################################################################

@app.route("/manageProfSlots", methods=["GET","POST"])
def manageProfSlots():
    if not session.get('username'):
        return redirect(url_for('login'))
    if session.get('role')=="staff":
        date = request.form.get('date')
        block = request.form.getlist('block')
        holidays = Holiday.objects().order_by("+date").all()
        holidaylist = []
        for holiday in holidays:
            d = holiday["date"].strftime("%m/%d/%Y")
            holidaylist.append(d)
        prof_id = Professor.objects(MailID=session.get('email')).first().prof_id
        if block:
            if Professorslot.objects.count() == 0:
                block_id = 1
            else:
                block_id = Professorslot.objects().order_by('-block_id').limit(-1).first().block_id + 1
            blockIndex = [int(i) for i in block]
            slots = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(len(slots)):
                if i in blockIndex:
                    slots[i] = 1
            dt = datetime.strptime(date, '%m/%d/%y').strftime('%Y-%m-%d %H:%M:%S.%f')
            if Professorslot.objects(prof_id=prof_id, date=dt):
                Professorslot.objects(prof_id=prof_id, date=dt,).update(slots=slots)
                profSlots = Professorslot.objects(prof_id=prof_id, date=date).first()
            else:
                Professorslot(block_id=block_id, prof_id=prof_id, date=dt, slots=slots).save()
            blockedSlots = []
            for i in range(len(slots)):
                if slots[i]==1 :
                    blockedSlots.append(slotsList[i])
            flash(f"Slots blocked by you for {date} : {blockedSlots} !","success")
            return render_template("manageprofslots.html", slotsList=slotsList, holidaylist=holidaylist, manageProfSlots=True, login=True)
        elif date:
            if Professorslot.objects(prof_id=prof_id, date=date):
                profSlots = Professorslot.objects(prof_id=prof_id, date=date).first()
            else:
                profSlots = dict({
                                    "slots": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                                })
            dt = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
            return render_template("manageprofslots.html", date=dt, prof_id=prof_id, profSlots=profSlots, slotsList=slotsList, holidaylist=holidaylist, manageProfSlots=True, login=True)
        else:
            return render_template("manageprofslots.html", slotsList=slotsList, holidaylist=holidaylist, manageProfSlots=True, login=True)


######################################################################
# COMPONENT  - STUDENTS & PROFESSORS : UPDATE PROFILE
# WRITTEN BY - DIVYA GOTTIMUKKALA & MRUDULA ANUMALA
# REVISED ON - OCT 24 2020
######################################################################

@app.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile(user_id = None):
    if not session.get('username'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    email = session.get('email')
    user = User.objects(email=email).first()
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.new_password.data :
            if form.current_password.data :
                if user.get_password(form.current_password.data):
                    if user.get_password(form.new_password.data):
                        flash("Your new password and old password cannot be same.","danger")
                    else:
                        user.set_password(form.new_password.data)
                        user.save()
                        flash("Your password was successfully changed.","success")
                else:
                    flash("Your current password is incorrect. Please try again","danger")
            else:
                flash("Please enter your current password","danger")

        if (user["first_name"] != form.first_name.data) and (user["last_name"] != form.last_name.data):
            User.objects(user_id=user_id).update(first_name=form.first_name.data, last_name=form.last_name.data)
            flash("Your first and last name are successfully changed.","success")
            if "my.unt.edu" not in email:
                Professor.objects(MailID=email).update(Name = form.first_name.data + " " + form.last_name.data)
                prof_id = Professor.objects(MailID=email).first().prof_id
                if Appointment.objects(prof_id=prof_id).first():
                    Appointment.objects(prof_id=prof_id).update(prof_name = form.first_name.data + " " + form.last_name.data)

        elif user["first_name"] != form.first_name.data :
            User.objects(user_id=user_id).update(first_name=form.first_name.data)
            flash("Your first name was successfully changed.","success")
            if "my.unt.edu" not in email:
                lastName = User.objects(email=email).first().last_name
                Professor.objects(MailID=email).update(Name = form.first_name.data + " " + lastName)
                prof_id = Professor.objects(MailID=email).first().prof_id
                if Appointment.objects(prof_id=prof_id).first():
                    Appointment.objects(prof_id=prof_id).update(prof_name = form.first_name.data + " " + lastName)

        elif user["last_name"] != form.last_name.data :
            User.objects(user_id=user_id).update(last_name=form.last_name.data)
            flash("Your last name was successfully changed.","success")
            if "my.unt.edu" not in email:
                firstName = User.objects(email=email).first().first_name
                Professor.objects(MailID=email).update(Name = firstName + " " + form.last_name.data)
                prof_id = Professor.objects(MailID=email).first().prof_id
                if Appointment.objects(prof_id=prof_id).first():
                    Appointment.objects(prof_id=prof_id).update(prof_name = firstName + " " + form.last_name.data)
        return redirect(url_for('updateprofile'))

    else:
        form.first_name.data = user["first_name"]
        form.last_name.data  = user["last_name"]
    return render_template('updateprofile.html', login = True, updateprofile = True, user_id = user_id, form = form)

######################################################################
# COMPONENT  - STUDENTS : CALENDAR VIEW
# WRITTEN BY - DIVYA GOTTIMUKKALA
# REVISED ON - NOV 8 2020
######################################################################
@app.route("/studentscalendar", methods=["GET"])
def studentscalendar():
    if not session.get('username'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    profs = list(User.objects.aggregate(*[
                {
                    '$lookup': {
                        'from': 'appointment',
                        'localField': 'user_id',
                        'foreignField': 'user_id',
                        'as': 'r1'
                    }
                },
                 {
                    '$unwind': {
                        'path': '$r1',
                        'includeArrayIndex': 'r1_id',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$sort': {
                        'r1.date': 1
                    }
                }, {
                    '$lookup': {
                        'from': 'professor',
                        'localField': 'r1.prof_id',
                        'foreignField': 'prof_id',
                        'as': 'r2'
                    }
                }, {
                    '$unwind': {
                        'path': '$r2',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$match': {
                        'user_id': user_id
                    }
                }, {
                    '$sort': {
                        'prof_id': 1
                    }
                }
            ]))
    return render_template("studentscalendar.html",  profs=json.dumps(profs, default=str), login=True, studentscalendar=True)

######################################################################
# COMPONENT  - PROFESSORS : CALENDAR VIEW
# WRITTEN BY - DIVYA GOTTIMUKKALA
# REVISED ON - NOV 8 2020
######################################################################
@app.route("/profcalendar", methods=["GET"])
def profcalendar():
    if not session.get('username'):
        return redirect(url_for('login'))
    Prof = Professor.objects(MailID=session.get('email')).first()
    prof_id = Prof.prof_id
    students = list(Professor.objects.aggregate(*[
                {
                    '$lookup': {
                        'from': 'appointment',
                        'localField': 'prof_id',
                        'foreignField': 'prof_id',
                        'as': 'r1'
                    }
                },
                 {
                    '$unwind': {
                        'path': '$r1',
                        'includeArrayIndex': 'r1_id',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$sort': {
                        'r1.date': 1
                    }
                }, {
                    '$lookup': {
                        'from': 'user',
                        'localField': 'r1.user_id',
                        'foreignField': 'user_id',
                        'as': 'r2'
                    }
                }, {
                    '$unwind': {
                        'path': '$r2',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$match': {
                        'prof_id': prof_id
                    }
                }, {
                    '$sort': {
                        'user_id': 1
                    }
                }
            ]))
    return render_template("profcalendar.html",  students=json.dumps(students, default=str), profcalendar=True, login=True, )


######################################################################
# COMPONENT  - ADMIN : VIEW SCHEDULED APPOINTMENTS
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 24 2020
######################################################################

@app.route("/adminhome", methods=["GET","POST"])
def adminhome():
    if not session.get('username'):
        return redirect(url_for('login'))
    if session.get('role')=="admin":
        AppointmentsData = Appointment.objects.order_by("-date")
        return render_template("adminhome.html", AppointmentsData=AppointmentsData, home=True, login=True )


######################################################################
# COMPONENT  - ADMIN : ADD HOLIDAYS
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - OCT 25 2020
######################################################################

@app.route("/addHolidays", methods=["GET","POST"])
def addHolidays():
    if not session.get('username'):
        return redirect(url_for('login'))
    if session.get('role')=="admin":
        holiday = request.form.get('holidayDate')
        deleteHoliday = request.form.get('deleteDate')
        if holiday:
            if Holiday.objects.count() == 0:
                holiday_id = 1
            else:
                holiday_id = Holiday.objects().order_by('-holiday_id').limit(-1).first().holiday_id + 1

            if Holiday.objects(date=holiday):
                flash(f"{holiday} is already added as holiday","danger")
            else:
                flash(f"{holiday} is added as a holiday","success")
                Holiday(holiday_id=holiday_id, date=holiday).save()
        if deleteHoliday:
                dt = datetime.strptime(deleteHoliday, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S.%f')
                Holiday.objects(date=dt).delete()
                flash(f"{deleteHoliday} is removed as a holiday !","success")
        holidays = Holiday.objects.order_by("+date")
        return render_template("addholidays.html", holidays=holidays, addholidays=True, login=True)


######################################################################
# COMPONENT  - ADMIN : VIEW USERS DETAILS
# WRITTEN BY - TANVEETA KATRAGADDA, MRUDULA ANUMALA
# REVISED ON - OCT 26 2020
######################################################################

@app.route("/usersDetails", methods=["GET","POST"])
def usersDetails():
    if not session.get('username'):
        return redirect(url_for('login'))
    if session.get('role')=="admin":
        UserData = User.objects.order_by("+user_id")
        roleOption = request.form.get('option')
    return render_template("usersdetails.html", users=UserData, usersdetails=True, login=True, option=roleOption )


######################################################################
# COMPONENT  - ADMIN : AUTHORIZE MAIL IDS
# WRITTEN BY - VASAVI KOLLA
# REVISED ON - OCT 28 2020
######################################################################

@app.route('/authorizeMailID', methods=["GET", "POST"])
def authorizeMailID():
    unsuccessfulEntries = {}
    form = AuthorizeMailForm()
    authorizedUsers = Universitymail.objects.order_by("+user_id")
    delete_authorized_user_id = request.form.get('deleteAuthorizedUser')
    role_DeleteUser = request.form.get('roleDeleteUser')
    email_DeleteUser = request.form.get('emailDeleteUser')
    roleOption = request.form.get('option')
    if delete_authorized_user_id:
        if role_DeleteUser == "admin":
            flash(f" Admin cannot be unauthorized by you!","danger")
        Universitymail.objects(user_id=delete_authorized_user_id).delete()
        flash(f" User with Email {email_DeleteUser} and id {delete_authorized_user_id} is unauthorized !","success")
        User.objects(email=email_DeleteUser).delete()
        if role_DeleteUser == "student":
            Appointment.objects(user_id=delete_authorized_user_id).delete()
        elif role_DeleteUser == "staff":
            if Professor.objects(MailID=email_DeleteUser).first():
                prof_id = Professor.objects(MailID=email_DeleteUser).first().prof_id
                Appointment.objects(prof_id=prof_id).delete()
                Professor.objects(prof_id=prof_id).delete()
                Professorslot.objects(prof_id=prof_id).delete()
        return render_template("authorizeMailID.html", login=True, authorizeMailID=True, unsuccessfulEntries = unsuccessfulEntries, authorizedUsers=authorizedUsers, form=form, option=roleOption )
    if "mailID_submit" in request.form and form.validate_on_submit():
        if request.values.get('email') == None:
            return render_template("authorizeMailID.html", login=True, authorizeMailID=True, unsuccessfulEntries = unsuccessfulEntries, authorizedUsers=authorizedUsers, form=form, option=roleOption )
        else:
            if not session.get('username'):
                return redirect(url_for('login'))
            if session.get('role')=="admin":
                input_emails = request.values.get("email")
                # Split by Space or Comma
                input_emails_list = ','.join(input_emails.split()).split(",")
                invalid_emails_list = []
                existing_users_list = []
                runtime_error_list = []
                successful_entries_list = []
                for input_email in input_emails_list:
                    if not input_email.endswith('@my.unt.edu')  and not input_email.endswith('@unt.edu'):
                        invalid_emails_list.append( input_email )
                    elif Universitymail.objects(email=input_email).count() == 1:
                        existing_users_list.append (input_email)
                    else:
                        new_user_id = Universitymail.objects.order_by('-user_id').first().user_id + 1
                        if not input_email.endswith('@my.unt.edu'):
                            new_email_insert = Universitymail(user_id = new_user_id, email = input_email, role = "staff")
                        else:
                            new_email_insert = Universitymail(user_id = new_user_id, email = input_email, role = "student")
                        new_email_insert.save()
                        successful_entries_list.append(input_email)
                        if not (Universitymail.objects(email=input_email).count() == 1):
                            runtime_error_list.append(input_email)
        unsuccessfulEntries.update(dict(zip(invalid_emails_list, ['Invalid Format' for i in range(len(invalid_emails_list))])))
        unsuccessfulEntries.update(dict(zip(existing_users_list, ['Already Exists' for i in range(len(existing_users_list))])))
        unsuccessfulEntries.update(dict(zip(runtime_error_list, ['Runtime Error' for i in range(len(runtime_error_list))])))
        if len(successful_entries_list) > 0:
            flash(f"{successful_entries_list} Email IDs are authorized !","success")
        if len(invalid_emails_list) > 0 or len(existing_users_list) > 0:
            flash(f"Please check the failed entries table for errors !","danger")
        form.email.data = ""
    else:
        return render_template("authorizeMailID.html", login=True, authorizeMailID=True, unsuccessfulEntries = unsuccessfulEntries, authorizedUsers=authorizedUsers, form=form, option=roleOption )
    return render_template("authorizeMailID.html",login=True, authorizeMailID=True, unsuccessfulEntries = unsuccessfulEntries.items(), authorizedUsers=authorizedUsers, form=form, option=roleOption )


######################################################################
# COMPONENT  - ADMIN : ADD PROFESSOR
# WRITTEN BY - TANVEETA KATRAGADDA
# REVISED ON - NOV 9 2020
######################################################################

@app.route("/addprofessor", methods=["GET","POST"])
def addprofessor():
    if not session.get('username'):
        return redirect(url_for('login'))
    if session.get('role')=="admin":
        form = ProfessorForm()
        if form.validate_on_submit():
            prof_id     = Professor.objects.count()
            prof_id     += 1
            Name        = form.Name.data
            Dept        = form.Dept.data
            Designation = form.Designation.data
            MailID      = form.MailID.data
            profExist = Professor.objects(MailID=MailID).first()
            if profExist:
                flash(f"Professor {Name} is added already !", "danger")
                return render_template("addprofessor.html", form=form, addprofessor=True)
            authProf = Universitymail.objects(email=MailID).first()
            if not authProf:
                flash(f"Professor {Name} must first be authorized & registered !", "danger")
                return render_template("addprofessor.html", form=form, addprofessor=True)
            profReg = User.objects(email=MailID).first()
            if not profReg:
                flash(f"Professor {Name} must first register to the application !", "danger")
                return render_template("addprofessor.html", form=form, addprofessor=True)
            if (not (MailID.count('@unt.edu') == 1)) or (not (MailID.endswith('@unt.edu'))) :
                flash("Invalid domain ! (UNT Professors domain is @unt.edu)","danger")
                return render_template("addprofessor.html", form=form, addprofessor=True)
            professor = Professor(prof_id=prof_id, Name=Name, Dept=Dept, Designation=Designation, MailID=MailID)
            professor.save()
            flash("Added Professor successfully!","success")
            form.Name.data = ""
            form.Dept.data = ""
            form.Designation.data = ""
            form.MailID.data = ""
        return render_template("addprofessor.html", form=form, addprofessor=True)


######################################################################
# COMPONENT  - USERS LOGOUT
# WRITTEN BY - MRUDULA ANUMALA
# REVISED ON - SEP 30 2020
######################################################################

@app.route("/logout")
def logout():
    session['user_id']=False
    session.pop('username',None)
    flash(f"You were logged out !","success")
    return redirect(url_for('index'))
