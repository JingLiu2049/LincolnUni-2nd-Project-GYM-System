from flask import Flask,url_for,session, redirect, flash,render_template,request
import datetime as dt
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import connect
import uuid
import re
from datetime import datetime, timedelta, date 
from dateutil.relativedelta import *
from flask_mail import Mail, Message


# from userimg import insert_userimg   




app = Flask(__name__)
app.secret_key = 'project1_group2'

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'finn.he0102@gmail.com'
# app.config['MAIL_PASSWORD'] = 'xxxxxxx'   # if you want to use it, please change the less security setting in google account and insert password here


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'esangkop@gmail.com'
app.config['MAIL_PASSWORD'] = 'xxxxxxxxx'   # if you want to use it, please change the less security setting in google account and insert password here

mail = Mail(app)

dbconn = None

""" All of our edit function will give a notification message to tell you know if you have edit successfully"""


""" The first part is connection part for our web, you can create a relation with database by it """


def getCursor():    
    global dbconn    
    if dbconn == None:
        conn = psycopg2.connect(dbname=connect.dbname, user=connect.dbuser, 
        password=connect.dbpass, host=connect.dbhost, port=connect.dbport)
        dbconn = conn.cursor()  
        #conn.autocommit = True

        return dbconn
    else:
        return dbconn

app.secret_key = 'project1_group2'


""" The second part is some function for after part using."""


def gen_id():                      # Generate id number automatically
    return uuid.uuid4().fields[2]

def strip(obj):
    obj_s = str(obj).lower()
    format = re.sub('[^a-z^]', '', obj_s)
    return format

def attend_times(attend_type, period):
            now_date = dt.datetime.now()
            then_date = now_date -  dt.timedelta(days= int(period))
            now = time.time()
            then = time.mktime(then_date.timetuple())
            attend_list = []
            for item in attend_type:
                date = str(item[0])
                class_time = time.mktime(time.strptime(date[0:10],"%Y-%m-%d"))
                if then < class_time < now:
                    attend_list.append(item)
            return len(attend_list)

def test(var,text):               # test function for developers testing if a variable is what they want.
    time = dt.datetime.today()
    print(var, type(var),time,text)


""" The third part is log in/out part"""


@app.route("/", methods=['GET', 'POST'])     #log in part for manager, trainer, member enter their own interface.
def login():
    if request.method == 'POST':
        useremail = request.form.get('useremail')
        password = request.form.get('password')
        test(useremail,'ddddddddddddddddddddddddddddddddddddddd')
        test(password,'ddddddddddddddddddddddddddddddddddddddd')
        cursor = getCursor()
        cursor.execute('SELECT * FROM login WHERE member_email = %s AND password \
            = %s;', (useremail, password, ))
        member = cursor.fetchone()
        cursor.execute('SELECT * FROM login WHERE trainer_email = %s AND password \
            = %s;', (useremail, password, ))
        trainer = cursor.fetchone()
        cursor.execute('SELECT * FROM login WHERE manager_email = %s AND password \
            = %s;', (useremail, password, ))
        manager = cursor.fetchone()
        account = False
        if member:
            account = member
        elif trainer:
            account = trainer
        elif manager:
            account = manager
        if account:
            session['loggedin'] = True
            session['usertype'] = account[2]
            session['date'] = str(dt.datetime.today())
            session['userid'] = account[0]
            if account[3]:
                sql = "SELECT first_name, last_name FROM member WHERE user_id = %s;" % account[0]
                cursor.execute(sql)
                name = cursor.fetchone()
                session['name'] = name
                return redirect(url_for('member'))
            elif account[4]:
                sql = "SELECT first_name, last_name FROM trainer WHERE user_id = %s;" % account[0]
                cursor.execute(sql)
                name = cursor.fetchone()
                session['name'] = name
                return redirect(url_for('trainer'))
            elif account[5]:
                sql = "SELECT first_name, last_name FROM manager WHERE user_id = %s;" % account[0]
                cursor.execute(sql)
                name = cursor.fetchone()
                session['name'] = name
                return redirect(url_for('manager'))
        else:
            flash('Invalid username or password. Please try again!')
            return redirect(url_for('login'))
    return render_template( 'login.html')

@app.route("/logout")              #log out part. You can log out at any time and protect your information security.
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('usertype', None)
    return redirect(url_for('login'))


""" From here we can start our web travel. """


@app.route("/manager")           # This is manager first interface 
def manager():
    return render_template( 'management_manager.html',usertype = session['usertype'], 
    name = session['name'])


""" The fourth part is for manager, you can manage member information. """


@app.route("/memberlist", methods = ['GET','POST'])    #this part is a member list, and you can enter update interface by clicking update button. you also can look a delete button in this interface.
def member_list():
    cur = getCursor()
    cur.execute("SELECT member.user_id as ID, first_name as FirstName, last_name as LastName, phone_number as Phone, email_address as Email, membership_type as Membership, membership_status as Status\
    from member LEFT JOIN authorisation on authorisation.user_id = member.user_id\
    LEFT JOIN membership on membership.user_id = member.user_id ORDER BY member.user_id;")
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template('memberlist.html',dbresult=select_result, dbcols=column_names, date=datetime.now(), usertype = session['usertype'], name = session['name'])   

@app.route("/member_search_list", methods = ['GET','POST'])      #this part is for searching a special recording 
def member_search_list():
    if request.method == 'POST':
        searchcondition_name = request.form.get('searchbox')
        print(searchcondition_name)
        cur = getCursor()
        cur.execute("select first_name from member")
        firstname_tuplelist = cur.fetchall()
        firstname_list = [j for i in firstname_tuplelist for j in i]
        if searchcondition_name in firstname_list:
            cur.execute("SELECT member.user_id as ID, first_name as FirstName, last_name as LastName, phone_number as Phone, email_address as Email, membership_type as Membership, membership_status as Status\
            from member JOIN authorisation on authorisation.user_id = member.user_id\
            JOIN membership on membership.user_id = member.user_id WHERE first_name=%s;",(searchcondition_name,))
            select_result1 = cur.fetchall()  
            column_names1 = [desc[0] for desc in cur.description]
            return render_template('memberlist.html',dbresult=select_result1, dbcols=column_names1,usertype = session['usertype'], name = session['name'], date=datetime.now())
        else:
            return redirect(url_for('member_list' ))

@app.route("/add_member_interface", methods = ['GET','POST'])    #this part is for add new trainer.
def add_member_interface():
    if request.method == 'POST':
        print(request.form)
        memberfirstname_given= request.form.get('firstname_member')
        memberlastname_given= request.form.get('lastname_member')
        memberphone_given= request.form.get('phonenumber_member')
        memberemail_given= request.form.get('email_member')
        memberaddress_given= request.form.get('address_member')
        memberbirthday_given= request.form.get('birthday_member')
        membergender_given= request.form.get('gender_member')
        membergoals_given= request.form.get('goals_member')
        membermedicalnotes_given= request.form.get('medicalnotes_member')
        memberphonto_given= request.form.get('photo_member')
        # memberstatus_given= request.form.get('status_member')
        membertype_given=request.form.get('usertype_member')
        # membermembership_given=request.form.get('membership_member')
        memberpassword_given=request.form.get('password_member')
        # returnbutton_given = request.args.get('returnid')
        join_date = request.form.get('joindate')
        member_type = request.form.get('type')
        quantity = int(request.form.get('quantity'))
        test(join_date,'6666666666666666666666666666666666')
        if member_type == 'weekly':
            duedate = datetime.strptime(join_date, '%Y-%m-%d')  + relativedelta(weeks=quantity)
        elif member_type == 'monthly':
            duedate = datetime.strptime(join_date, '%Y-%m-%d')  + relativedelta(months=quantity)
        elif member_type == 'yearly':
            duedate = datetime.strptime(join_date, '%Y-%m-%d')  + relativedelta(years=quantity)
            
        test(duedate,'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')
        # print(returnbutton_given)
        # if returnbutton_given == 'return':
        #     return redirect(url_for('member_list' ))
        cur = getCursor()
        cur.execute("INSERT INTO authorisation VALUES (nextval('mem_id_seq'), %s, %s) \
            RETURNING user_id;",(memberpassword_given, membertype_given,))
        userid = cur.fetchone()[0]
        print(userid,type(userid),'ooooooooooooooooooooooooooooooooooooooooooooooooooo')
        cur.execute("INSERT INTO member VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (
            userid,memberfirstname_given,memberlastname_given,memberphone_given,memberemail_given,
            memberaddress_given,memberbirthday_given,membergender_given,membergoals_given,
            membermedicalnotes_given,memberphonto_given,))  
        sql = "INSERT INTO membership VALUES (%s, '%s', null, '%s', 'active', '%s', 0,0)" %(userid, member_type,join_date,duedate)   
        cur.execute(sql)
        flash("Successfully!  You have added %s !" % (memberfirstname_given,))
        return redirect(url_for('member_list' ))
    return render_template('addnewmember.html', usertype = session['usertype'], name = session['name'],today = dt.datetime.today())

@app.route("/update_member_interface", methods = ['GET','POST'])  #this part is for update trainer.
def update_member_interface():
    if request.method == 'POST':
        memberid_given1 = request.form.get('userid_update')  
        print(memberid_given1)      
        memberfirstname_given1= request.form.get('first_name_update')
        memberlastname_given1= request.form.get('last_name_update')
        memberphone_given1= request.form.get('phone_number_update')
        memberemail_given1= request.form.get('email_address_update')
        memberaddress_given1= request.form.get('address_update')
        memberbirthday_given1= request.form.get('birthday_update')
        membergender_given1= request.form.get('gender_update')
        membergoals_given1= request.form.get('goals_update')
        membermedicalnotes_given1= request.form.get('medical_notes_update')
        memberphonto_given1= request.form.get('photo_url_update')
        membertype_given1=request.form.get('user_type_update')
        membermembership_given1=request.form.get('membership_type_update')
        print(membermembership_given1)
        memberpassword_given1=request.form.get('password_update')
        print(memberpassword_given1)
        cur = getCursor()
        cur.execute("UPDATE member SET first_name=%s,last_name=%s,phone_number=%s,\
            email_address=%s,address=%s,date_of_birth=%s,gender=%s,goals=%s, medical_notes=%s, \
                photo_url=%s WHERE member.user_id=%s;",(memberfirstname_given1,
                memberlastname_given1,memberphone_given1,memberemail_given1,memberaddress_given1,
                memberbirthday_given1,membergender_given1,membergoals_given1,membermedicalnotes_given1,
                memberphonto_given1,memberid_given1,))
        cur.execute("UPDATE membership SET membership_type=%s WHERE membership.user_id=%s;"
                    ,(membermembership_given1,memberid_given1,))
        cur.execute("UPDATE authorisation SET password=%s, user_type=%s WHERE authorisation.user_id=%s;"
                    , (memberpassword_given1, membertype_given1,memberid_given1,))
        session['successs'] = True
        flash('Successfully Update! You have Updated %s!' % (memberfirstname_given1,))
        return redirect(url_for('member_list' ))
    else:
        needtobeupdated_id = request.args.get('correspondingid')
        print(needtobeupdated_id)
        cur = getCursor()
        cur.execute("SELECT * FROM listmember WHERE listmember.user_id=%s;",(needtobeupdated_id,))
        select_result_update = cur.fetchall() 
        column_names_update = [desc[0] for desc in cur.description]
        return render_template('update_member_interface.html',dbresult_update=select_result_update, dbcols_update=column_names_update,usertype = session['usertype'], name = session['name'])

@app.route("/delete_member_interface", methods = ['GET','POST'])  #this part is for delete member actually it just make member status become inactive.
def delete_member_interface():
    needtobedeleted_id = request.args.get('correspondingid_d')
    print(needtobedeleted_id)
    if needtobedeleted_id is not None:
        cur = getCursor()
        cur.execute("UPDATE membership SET membership_status='inactivate' WHERE membership.user_id=%s;",(needtobedeleted_id,))
        session['successs'] = True
        flash('Successfully Deleted! You have deleted %s!' % (needtobedeleted_id,))
        return redirect(url_for('member_list' ))
    else:
        return redirect(url_for('member_list' ))

@app.route("/attendance_review/member", methods = ['GET','POST'])  # this part if for manager view member's attendance, there are data tabel and dynamic bar chart.
def attendance_member():
    cursor = getCursor()
    sql = "select class_year,class_month, count(group_class_date) from group_attendance \
        group by class_year, class_month order by class_year DESC, class_month DESC;"
    cursor.execute(sql)
    group_attend = cursor.fetchall()
   
    list1_p=[list(elem) for elem in group_attend]
    list_p_year,list_p_month,list_p_num=[],[],[]
    for x,y,z in list1_p:
        list_p_year.append(x)
        list_p_month.append(y)
        list_p_num.append(z)
    print(list_p_year)
    print(list_p_month)
    print(list_p_num)
    sdhusd=[int(ee) for ee in list_p_year]
    list_p_year_new = [str(yy) for yy in sdhusd]
    list_p_month_new =[int(xx) for xx in list_p_month]
    print(list_p_month_new)
    date_ym=[]
    month_str=[]
    monthdic={1:'.01', 2:'.02',3:'.03',4:'.04',5:'.05',6:'.06',7:'.07',8:'.08',9:'.09',10:'.10',11:'.11',12:'.12'}
    for t in list_p_month_new:
        month_str.append(monthdic[t])
    print(month_str)

    for i in range(0,len(list_p_year_new)):
        date_ym.append(list_p_year_new[i]+month_str[i])
    date_ym_int=[float(zz) for zz in date_ym]
    
    print(date_ym)

    print(group_attend)
    sql = "select class_year,class_month, count(pt_class_date) from pt_attendance \
        group by class_year, class_month order by class_year DESC, class_month DESC;"
    cursor.execute(sql)
    pt_attend = cursor.fetchall()
    print(pt_attend)
   
    list1_pt=[list(elemt) for elemt in pt_attend]
    list_pt_year,list_pt_month,list_pt_num=[],[],[]
    for xt,yt,zt in list1_pt:
        list_pt_year.append(xt)
        list_pt_month.append(yt)
        list_pt_num.append(zt)
    print(list_pt_year)
    print(list_pt_month)
    print(list_pt_num)
    sdhusdt=[int(eet) for eet in list_pt_year]
    list_pt_year_new = [str(yyt) for yyt in sdhusdt]
    list_pt_month_new =[int(xxt) for xxt in list_pt_month]
    print(list_pt_month_new)
    date_ymt=[]
    month_strt=[]
    monthdict={1:'.01', 2:'.02',3:'.03',4:'.04',5:'.05',6:'.06',7:'.07',8:'.08',9:'.09',10:'.10',11:'.11',12:'.12'}
    for tt in list_pt_month_new:
        month_strt.append(monthdict[tt])
    print(month_strt)

    for i in range(0,len(list_pt_year_new)):
        date_ymt.append(list_pt_year_new[i]+month_strt[i])
    date_ymt_int=[float(zzt) for zzt in date_ymt]
    
    print(date_ymt)

    
    sql = "SELECT extract(YEAR from gym_attendance_date)AS attend_year,  extract\
        (MONTH from gym_attendance_date)AS attend_month, count(gym_attendance_date) \
        from attendance group by  extract( YEAR from gym_attendance_date),extract\
        (MONTH from gym_attendance_date) order by extract(YEAR from gym_attendance_date) \
        DESC,extract(MONTH from gym_attendance_date) DESC;"
    cursor.execute(sql)
    total_attend = cursor.fetchall()
    print(total_attend)
    
    list1_pto=[list(elemto) for elemto in total_attend]
    list_pto_year,list_pto_month,list_pto_num=[],[],[]
    for xto,yto,zto in list1_pto:
        list_pto_year.append(xto)
        list_pto_month.append(yto)
        list_pto_num.append(zto)
    print(list_pto_year)
    print(list_pto_month)
    print(list_pto_num)
    sdhusdto=[int(eeto) for eeto in list_pto_year]
    list_pto_year_new = [str(yyto) for yyto in sdhusdto]
    list_pto_month_new =[int(xxto) for xxto in list_pto_month]
    print(list_pto_month_new)
    date_ymto=[]
    month_strto=[]
    monthdicto={1:'.01', 2:'.02',3:'.03',4:'.04',5:'.05',6:'.06',7:'.07',8:'.08',9:'.09',10:'.10',11:'.11',12:'.12'}
    for tto in list_pto_month_new:
        month_strto.append(monthdicto[tto])
    print(month_strto)

    for i in range(0,len(list_pto_year_new)):
        date_ymto.append(list_pto_year_new[i]+month_strto[i])
    date_ymto_int=[float(zzo) for zzo in date_ymto]
    
    print(date_ym)


    customised = False
    if request.method == 'POST':
        start = request.form.get('start')
        end = request.form.get('end')
        sql = "select count(pt_class_date) from booked_pt where attendance_status = \
            'present' and  (pt_class_date <= '%s' and pt_class_date >= '%s');" % (end,start)
        cursor.execute(sql)
        pts = str(cursor.fetchone()[0])
        sql = "select count(group_class_date) from booked_group where attendance_status = \
            'present' and (to_date(group_class_date, 'yyyy-mm-dd')<= '%s' \
            and to_date(group_class_date, 'yyyy-mm-dd')>= '%s' );"% (end,start)
        cursor.execute(sql)
        groups = str(cursor.fetchone()[0])
        sql = "select count(gym_attendance_date) from attendance where \
            (gym_attendance_date<= '%s' and gym_attendance_date >= '%s');" % (end,start)
        cursor.execute(sql)
        total = str(cursor.fetchone()[0])
        customised = [start, end, total, groups, pts]
    return render_template('attendance_member.html',usertype = session['usertype'], 
    name = session['name'], group_attend = group_attend, pt_attend = pt_attend,total_attend = total_attend,
    cust = customised, gclassdate=date_ym_int, gclassnum=list_p_num,gclassdatet=date_ymt_int, gclassnumt=list_pt_num,gclassdateto=date_ymto_int, gclassnumto=list_pto_num)

@app.route("/membership_list_manager", methods = ['GET','POST']) # this part is for the manager to check which members’ membership status will expire, and there is a button link to view the details of the specific members. 
def membership_list_manager():
    cur = getCursor()
    
    cur.execute("select user_id, first_name, membership_type, join_date, left_date, \
        membership_status from membershiplist where (membership_type='weekly' and \
        (membership_dueday-current_date)<= 3) or (membership_type='monthly' and \
        (membership_dueday-current_date)<=  7) or (membership_type = 'yearly' and \
        (membership_dueday-current_date) <= 15);")


    membership_select = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    memberidfromhtml = request.args.get('compariedid')
    print(memberidfromhtml)
    if memberidfromhtml is not None:
        cur = getCursor()
        cur.execute("select first_name from member where user_id=%s",(memberidfromhtml,))
        membername = cur.fetchall()
        membername_select = [j for i in membername for j in i]
        Firstname = membername_select[0]
        """ This part is for everything about payment date below"""
        cur = getCursor()
        cur.execute("select membership_type from membership where user_id=%s",(memberidfromhtml,))
        membershiptype = cur.fetchall()
        membershiptype_select = [j for i in membershiptype for j in i]
        membershiptype_result = membershiptype_select[0]   ### convert list into str
        print(membershiptype_result)
        cur.execute("select payment_date from membership_payment where user_id=%s",(memberidfromhtml,))
        paydate = cur.fetchall()
        paydate_select = [j for i in paydate for j in i]   # convert tuple list into pure list
        cur.execute("select membership_dueday from membership where user_id=%s",(memberidfromhtml,))
        lastduedate = cur.fetchall()
        lastduedate_select = [j for i in lastduedate for j in i]
        lastduedate_string = str(lastduedate_select[0])
        datedetail = dt.datetime.strptime(str(lastduedate_select[0]), '%Y-%m-%d')
        dateyear = datedetail.year
        datemonth = datedetail.month
        dateday = datedetail.day
        lastduedate_datetime = datetime(dateyear,datemonth,dateday)
        remained_detail_temporary = lastduedate_datetime - datetime.now()  
        if lastduedate_datetime >= datetime.now():                      
            remained_detail = remained_detail_temporary                 
        else:                                                            
            remained_detail = "0 day"        
        print(remained_detail)
        print(type(remained_detail))
        cur.execute("select outstanding_amount from membership WHERE user_id=%s",(memberidfromhtml,))
        outstandinginformation = cur.fetchall()
        outstanding_select = [j for i in outstandinginformation for j in i]
        outstanding_balance = outstanding_select[0]
        cur.execute("select balance  from membership WHERE user_id=%s",(memberidfromhtml,))
        balanceinformation = cur.fetchall()
        balance_select = [j for i in balanceinformation for j in i]
        just_balance_result = balance_select[0]
        return render_template('payment_information_manager.html', Member_id_display = memberidfromhtml, name_display = Firstname, lastdate = paydate_select[0], membershiptype_result=membershiptype_select[0], duedate=lastduedate_string[0:11], remained_day = str(remained_detail)[0:9], os_balance=outstanding_balance, just_balance=just_balance_result, date=datetime.now(),usertype = session['usertype'], name = session['name'])
    else:    
        return render_template('membership_list_manager.html',dbresult=membership_select, dbcols=column_names,date=datetime.now(),usertype = session['usertype'], name = session['name'])

@app.route("/payment_reminder", methods = ['GET','POST'])  # this part is email function for remind member "your membership is going to expire"
def payment_reminder():
    if request.method == 'POST':
        memberid_reminder = request.form.get('paymentmemberid')
        print(memberid_reminder)
        name_reminder = request.form.get('paymentmembername')
        duedate_reminder = request.form.get('paymentduedate')
        cur = getCursor()
        cur.execute("SELECT email_address FROM member WHERE user_id = %s;",(memberid_reminder,))
        email_select = cur.fetchall()
        email_listtype = [j for i in email_select for j in i]
        email_receive = email_listtype[0]
        print(email_receive)
        message = Message(subject='Member expiration reminder',sender = 'finn.he0102@gmail.com', recipients=[email_receive],body='Hi,%s. Your membership will expire at %s !' % (name_reminder,duedate_reminder,))    
        try:        
            mail.send(message)        
            session['successs'] = True
            flash('Successfully! You have sent reminder email to  %s !' % (name_reminder,))
            return redirect(url_for('membership_list_manager' ))     
        except Exception as e:        
            print(e)        
            session['successs'] = True
            flash('Sorry! The reminder email to  %s unsuccessfully!' % (name_reminder,))
            return redirect(url_for('membership_list_manager' )) 

@app.route("/contact_members", methods=['GET', 'POST'])   # this part is for manager to select member you want to communicate with.
def contact_members():    
    cur = getCursor()
    cur.execute("SELECT user_id, first_name, last_name, email_address FROM member;")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template('contact_members.html',dbresult=select_result,dbcols=column_names, \
        usertype = session['usertype'], name = session['name'])

@app.route("/contact_members/email", methods=['GET', 'POST'])  # this part is for email interface to get email address and add them to email recipient box.
def contact_members_email(): 
    if request.method == 'POST':    

       recipientslist = request.form.getlist('recipients')
       separator = ', '
       print(recipientslist)
       print(type(recipientslist))
 
       recipients = separator.join(recipientslist)
       print(recipients)
       print(type(recipients))
        
    return render_template('contact_members_email.html',  recipients=recipients,
        usertype = session['usertype'], name = session['name'])

@app.route("/contact_members/send_email", methods=['GET','POST'])  # this part is for manager to send email to which you want.
def contact_members_send_email(): 
    if request.method == 'POST':
        
        sent = dt.datetime.now()
        email_subject = request.form.get('subject')
        email_message = request.form.get('message')
        sender = request.form.get('sender')
        recipients = request.form.getlist('recipients')
        
        print(sent)
        print(email_subject)
        print(sender)
        print(email_message)
        print(recipients)
        print(type(recipients))

        with mail.connect() as conn:
            for recipient in recipients:
                message = Message (
                    subject=email_subject,
                    sender='esangkop@gmail.com', 
                    recipients=[recipient],
                    body=email_message
                    ) 
                conn.send(message)

                cur = getCursor()
                cur.execute("INSERT INTO communication(sent, sender, subject, message) \
                    VALUES (%s,%s,%s,%s);",(sent,sender,email_subject,email_message,))


                flash ('Email was successfully sent!')
               
                return render_template('contact_members_email.html', 
                usertype = session['usertype'], name = session['name'])


""" The fifth part is for manager, you can manage trainer information. """


@app.route("/trainer_list", methods = ['GET','POST'])      #this part is a trainer list, and you can enter update interface by clicking update button. you also can look a delete button in this interface.
def trainer_list():
    cur = getCursor()
    cur.execute("select trainer.user_id, first_name, last_name, phone_number, email_address, status\
    from trainer")
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template( 'trainer_list.html',dbresult=select_result, dbcols=column_names, 
    usertype = session['usertype'], name = session['name'] )    

@app.route("/trainer_search_list", methods = ['GET','POST']) #this part is for searching a special recording and return to the corresponding delete interface.The action is just related with the same delete action above when it enter the the corresponding delete interface, because the special recording table is also in same action form of the same delete interface 
def trainer_search_list():
    if request.method == 'POST':
        searchcondition_name = request.form.get('searchbox')
        print(searchcondition_name)
        cur = getCursor()
        cur.execute("select first_name from trainer")
        firstname_tuplelist = cur.fetchall()
        firstname_list = [j for i in firstname_tuplelist for j in i]
        if searchcondition_name in firstname_list:
            cur.execute("select trainer.user_id, first_name, last_name, phone_number, email_address, status\
            from trainer WHERE first_name=%s;",(searchcondition_name,))
            select_result1 = cur.fetchall()
            # print(select_result1)  
            column_names1 = [desc[0] for desc in cur.description]
            return render_template('trainer_list.html',dbresult=select_result1, 
            dbcols=column_names1,usertype = session['usertype'], name = session['name'])
        else:
            return redirect(url_for('trainer_list' ))

@app.route("/add_trainer_interface", methods = ['GET','POST']) #this part is for add new trainer
def add_trainer_interface():
    if request.method == 'POST':
        print(request.form)    
        trainerfirstname_given= request.form.get('firstname_trainer')
        trainerlastname_given= request.form.get('lastname_trainer')
        trainerphone_given= request.form.get('phonenumber_trainer')
        traineremail_given= request.form.get('email_trainer')
        traineraddress_given= request.form.get('address_trainer')
        trainerbirthday_given= request.form.get('birthday_trainer')
        trainergender_given= request.form.get('gender_trainer')
        trainerspecialty_given= request.form.get('specialty_trainer')
        trainerexperience_given= request.form.get('experience_trainer')
        trainercertification_given= request.form.get('certification_trainer')
        trainerphonto_given= request.form.get('photo_trainer')
        trainertype_given=request.form.get('usertype_trainer')
        trainerpassword_given=request.form.get('password_trainer')
        cur = getCursor()
        cur.execute("INSERT INTO authorisation VALUES (nextval('trainer_id_seq'), %s, %s) \
            RETURNING user_id;",(trainerpassword_given, trainertype_given,))
        userid = cur.fetchone()[0]
        test(userid,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')

        cur.execute("INSERT INTO trainer VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",\
                (userid,trainerfirstname_given,trainerlastname_given,trainerphone_given,
                traineremail_given,traineraddress_given,trainerbirthday_given,trainergender_given,
                trainerspecialty_given,trainerexperience_given,trainercertification_given,trainerphonto_given,))     
        session['successs'] = True
        flash("Successfully!  You have added %s !" % (trainerfirstname_given,))
        return redirect(url_for('trainer_list' ))
    else:
        return render_template('addnewtrainer.html',usertype = session['usertype'], name = session['name'])

@app.route("/update_trainer_interface", methods = ['GET','POST']) #this part is for update trainer
def update_trainer_interface():
    if request.method == 'POST':
        trainerid_given1 = request.form.get('userid_update')  ###### waiting for changing
        print(trainerid_given1)      
        trainerfirstname_given1= request.form.get('first_name_update')
        print(trainerfirstname_given1)
        trainerlastname_given1= request.form.get('last_name_update')
        trainerphone_given1= request.form.get('phone_number_update')
        traineremail_given1= request.form.get('email_addressr_update')
        traineraddress_given1= request.form.get('address_update')
        trainerbirthday_given1= request.form.get('birthday_update')
        trainergender_given1= request.form.get('gender_update')
        trainerspecialty_given1= request.form.get('specialty_update')
        trainerexperience_given1= request.form.get('experience_update')
        trainercertification_given1= request.form.get('certification_update')
        trainerphonto_given1= request.form.get('photo_url_update')
        trainertype_given1=request.form.get('user_type_update')
        trainerpassword_given1=request.form.get('password_update')
        cur = getCursor()
        cur.execute("UPDATE trainer SET first_name=%s,last_name=%s,phone_number=%s,email_address=%s,\
            address=%s,date_of_birth=%s,gender=%s,specialty=%s, years_of_experience=%s, certification=%s, \
                photo_url=%s WHERE user_id=%s;",(trainerfirstname_given1,trainerlastname_given1,trainerphone_given1,
                traineremail_given1,traineraddress_given1,trainerbirthday_given1,trainergender_given1,
                trainerspecialty_given1,trainerexperience_given1,trainercertification_given1,trainerphonto_given1,trainerid_given1))
        cur.execute("UPDATE authorisation SET password=%s, user_type=%s WHERE authorisation.user_id=%s;"
                    , (trainerpassword_given1, trainertype_given1,trainerid_given1,))

        session['successs'] = True
        flash('Successfully Update! You have Updated %s!' % (trainerfirstname_given1,))
        return redirect(url_for('trainer_list' ))
    else:
        cur = getCursor()
        needtobeupdated_id = request.args.get('correspondingid')
        print(needtobeupdated_id)
        cur.execute("SELECT * FROM trainer WHERE user_id=%s;",(needtobeupdated_id,))
        cur.execute("DROP VIEW IF EXISTS listtrainer CASCADE;")
        cur.execute("create view listtrainer as select trainer.user_id, first_name, \
            last_name, phone_number, email_address, address, date_of_birth, gender, specialty, \
            years_of_experience, certification, \
        photo_url, user_type, password from trainer\
        join authorisation on authorisation.user_id = trainer.user_id;")
        cur.execute("SELECT * FROM listtrainer WHERE listtrainer.user_id=%s;",(needtobeupdated_id,))
        select_result_update = cur.fetchall() 
        column_names_update = [desc[0] for desc in cur.description]
        return render_template('update_trainer_interface.html',dbresult_update=select_result_update, dbcols_update=column_names_update,usertype = session['usertype'], name = session['name'] )

@app.route("/delete_trainer_interface", methods = ['GET','POST']) #this part is for delete trainer
def delete_trainer_interface():
    if request.method == 'POST':
        needtobedeleted_id = request.form.get('correspondingid_d')
        print(needtobedeleted_id)
        cur = getCursor()
        cur.execute("UPDATE trainer SET status='inactive' WHERE trainer.user_id=%s;",(needtobedeleted_id,))
        session['successs'] = True
        flash('Successfully Deleted! You have deleted %s!' % (needtobedeleted_id,))
        return redirect(url_for('trainer_list' ))
    else:
        return redirect(url_for('trainer_list' ))


""" The sixth part is for manager, you can manage public class information. """


@app.route("/public_class_manager", methods = ['GET','POST'])   # this part is for manager to view class distribution and detail information in timetable, there are also three button link to add, update and delete interface.
def public_class_manager():
    returnbutton_given = request.args.get('returnid')
    print(returnbutton_given)
    if returnbutton_given == 'return':
        return redirect(url_for('public_class_manager' ))
    #timetable part
    cur = getCursor()
    cur.execute("select group_class_name,group_class_date,group_class_day,group_class_id, \
        group_class_start_time,group_class_end_time from group_class")
    class_basic_select = cur.fetchall()
    print(class_basic_select)

    
    idfromhtml = request.args.get('compareid')
    cur = getCursor()
    cur.execute("SELECT group_class_id, group_class_name, description, maximum_number, location, group_class_date, group_class_day,group_class_start_time, group_class_end_time,trainer_name, trainer_email FROM class_display WHERE group_class_id=%s",(idfromhtml,))
    class_detail_selected = cur.fetchall()
    selected_temporary = [j for i in class_detail_selected for j in i]
    
    week_day_dict = {1 : 'Monday', 2 : 'Tuesday', 3 : 'Wednesday', 4 : 'Thursday', 5 : 'Friday', 6 : 'Saturday', 7 : 'Sunday'}
    if idfromhtml is not None:
        selecteddate_str = selected_temporary[5]
        temporaryselect_date=dt.datetime.strptime(selecteddate_str, '%Y-%m-%d')
        print(temporaryselect_date)
        selectedyear=temporaryselect_date.year
        selectedmonth=temporaryselect_date.month
        selectedday=temporaryselect_date.day
        selecteddate_temporary=datetime(selectedyear,selectedmonth,selectedday)
        selecteddate_int=selecteddate_temporary.isoweekday()
        if selecteddate_int == 1:
            selecteddate_date = selecteddate_temporary
        elif selecteddate_int == 2:
            selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-1)
        elif selecteddate_int == 3:
            selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-2)    
        elif selecteddate_int == 4:
            selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-3)
        elif selecteddate_int == 5:
            selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-4)
        elif selecteddate_int == 6:
            selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-5)
        elif selecteddate_int == 7:
            selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-6)
        

        firstdate=selecteddate_date
        #datedetail = dt.datetime.strptime(str(firstdate), '%Y-%m-%d %H:%M:%S.%f')
        dateyear = firstdate.year
        datemonth = firstdate.month
        dateday = firstdate.day
        temporary_date_YMD = str(datetime(dateyear,datemonth,dateday))
        date_YMD = temporary_date_YMD[0:10]
        firstdateweekday_int=firstdate.isoweekday()
        firstdateweekday_str=week_day_dict[firstdateweekday_int]  # list2 firstweeklist_weekday

        seconddate = firstdate + dt.timedelta(days=+1)
        dateyear2 = seconddate.year
        datemonth2 = seconddate.month
        dateday2 = seconddate.day
        temporary_date_YMD2 = str(datetime(dateyear2,datemonth2,dateday2))
        date_YMD2 = temporary_date_YMD2[0:10]
        seconddateweekday_int=seconddate.isoweekday()
        seconddateweekday_str=week_day_dict[seconddateweekday_int]  # list2 firstweeklist_weekday

        thirddate = firstdate + dt.timedelta(days=+2)
        dateyear3 = thirddate.year
        datemonth3 = thirddate.month
        dateday3 = thirddate.day
        temporary_date_YMD3 = str(datetime(dateyear3,datemonth3,dateday3))
        date_YMD3 = temporary_date_YMD3[0:10]
        thirddateweekday_int=thirddate.isoweekday()
        thirddateweekday_str=week_day_dict[thirddateweekday_int]  # list2 firstweeklist_weekday

        fourthdate = firstdate + dt.timedelta(days=+3)
        dateyear4 = fourthdate.year
        datemonth4 = fourthdate.month
        dateday4 = fourthdate.day
        temporary_date_YMD4 = str(datetime(dateyear4,datemonth4,dateday4))
        date_YMD4 = temporary_date_YMD4[0:10]
        fourthdateweekday_int=fourthdate.isoweekday()
        fourthdateweekday_str=week_day_dict[fourthdateweekday_int]  # list2 firstweeklist_weekday

        fifthdate = firstdate + dt.timedelta(days=+4)
        dateyear5 = fifthdate.year
        datemonth5 = fifthdate.month
        dateday5 = fifthdate.day
        temporary_date_YMD5 = str(datetime(dateyear5,datemonth5,dateday5))
        date_YMD5 = temporary_date_YMD5[0:10]
        fifthdateweekday_int=fifthdate.isoweekday()
        fifthdateweekday_str=week_day_dict[fifthdateweekday_int]  # list2 firstweeklist_weekday

        sixthdate = firstdate + dt.timedelta(days=+5)
        dateyear6 = sixthdate.year
        datemonth6 = sixthdate.month
        dateday6 = sixthdate.day
        temporary_date_YMD6 = str(datetime(dateyear6,datemonth6,dateday6))
        date_YMD6 = temporary_date_YMD6[0:10]
        sixthdateweekday_int=sixthdate.isoweekday()
        sixthdateweekday_str=week_day_dict[sixthdateweekday_int]  # list2 firstweeklist_weekday

        seventhdate = firstdate + dt.timedelta(days=+6)
        dateyear7 = seventhdate.year
        datemonth7 = seventhdate.month
        dateday7 = seventhdate.day
        temporary_date_YMD7 = str(datetime(dateyear7,datemonth7,dateday7))
        date_YMD7 = temporary_date_YMD7[0:10]
        seventhdateweekday_int=seventhdate.isoweekday()
        seventhdateweekday_str=week_day_dict[seventhdateweekday_int]  # list2 firstweeklist_weekday
    
    
    elif idfromhtml is None:
        originaldate = datetime.now()
        temporaryoriginal_date=dt.datetime.strptime(str(originaldate), '%Y-%m-%d %H:%M:%S.%f')
        print(temporaryoriginal_date)
        originalyear=temporaryoriginal_date.year
        originalmonth=temporaryoriginal_date.month
        originalday=temporaryoriginal_date.day
        temporaryoriginal_date2=datetime(originalyear,originalmonth,originalday)
        originaldate_int=temporaryoriginal_date2.isoweekday()
        if originaldate_int == 1:
            finaloriginal_date = temporaryoriginal_date2
        elif originaldate_int == 2:
            finaloriginal_date = temporaryoriginal_date2+ dt.timedelta(days=-1)
        elif originaldate_int == 3:
            finaloriginal_date = temporaryoriginal_date2+ dt.timedelta(days=-2)    
        elif originaldate_int == 4:
            finaloriginal_date = temporaryoriginal_date2+ dt.timedelta(days=-3)
        elif originaldate_int == 5:
            finaloriginal_date = temporaryoriginal_date2+ dt.timedelta(days=-4)
        elif originaldate_int == 6:
            finaloriginal_date = temporaryoriginal_date2+ dt.timedelta(days=-5)
        elif originaldate_int == 7:
            finaloriginal_date = temporaryoriginal_date2+ dt.timedelta(days=-6)



        firstdate=finaloriginal_date
        #datedetail = dt.datetime.strptime(str(firstdate), '%Y-%m-%d %H:%M:%S.%f')
        dateyear = firstdate.year
        datemonth = firstdate.month
        dateday = firstdate.day
        temporary_date_YMD = str(datetime(dateyear,datemonth,dateday))
        date_YMD = temporary_date_YMD[0:10]
        firstdateweekday_int=firstdate.isoweekday()
        firstdateweekday_str=week_day_dict[firstdateweekday_int]  # list2 firstweeklist_weekday

        seconddate = firstdate + dt.timedelta(days=+1)
        dateyear2 = seconddate.year
        datemonth2 = seconddate.month
        dateday2 = seconddate.day
        temporary_date_YMD2 = str(datetime(dateyear2,datemonth2,dateday2))
        date_YMD2 = temporary_date_YMD2[0:10]
        seconddateweekday_int=seconddate.isoweekday()
        seconddateweekday_str=week_day_dict[seconddateweekday_int]  # list2 firstweeklist_weekday

        thirddate = firstdate + dt.timedelta(days=+2)
        dateyear3 = thirddate.year
        datemonth3 = thirddate.month
        dateday3 = thirddate.day
        temporary_date_YMD3 = str(datetime(dateyear3,datemonth3,dateday3))
        date_YMD3 = temporary_date_YMD3[0:10]
        thirddateweekday_int=thirddate.isoweekday()
        thirddateweekday_str=week_day_dict[thirddateweekday_int]  # list2 firstweeklist_weekday

        fourthdate = firstdate + dt.timedelta(days=+3)
        dateyear4 = fourthdate.year
        datemonth4 = fourthdate.month
        dateday4 = fourthdate.day
        temporary_date_YMD4 = str(datetime(dateyear4,datemonth4,dateday4))
        date_YMD4 = temporary_date_YMD4[0:10]
        fourthdateweekday_int=fourthdate.isoweekday()
        fourthdateweekday_str=week_day_dict[fourthdateweekday_int]  # list2 firstweeklist_weekday

        fifthdate = firstdate + dt.timedelta(days=+4)
        dateyear5 = fifthdate.year
        datemonth5 = fifthdate.month
        dateday5 = fifthdate.day
        temporary_date_YMD5 = str(datetime(dateyear5,datemonth5,dateday5))
        date_YMD5 = temporary_date_YMD5[0:10]
        fifthdateweekday_int=fifthdate.isoweekday()
        fifthdateweekday_str=week_day_dict[fifthdateweekday_int]  # list2 firstweeklist_weekday

        sixthdate = firstdate + dt.timedelta(days=+5)
        dateyear6 = sixthdate.year
        datemonth6 = sixthdate.month
        dateday6 = sixthdate.day
        temporary_date_YMD6 = str(datetime(dateyear6,datemonth6,dateday6))
        date_YMD6 = temporary_date_YMD6[0:10]
        sixthdateweekday_int=sixthdate.isoweekday()
        sixthdateweekday_str=week_day_dict[sixthdateweekday_int]  # list2 firstweeklist_weekday

        seventhdate = firstdate + dt.timedelta(days=+6)
        dateyear7 = seventhdate.year
        datemonth7 = seventhdate.month
        dateday7 = seventhdate.day
        temporary_date_YMD7 = str(datetime(dateyear7,datemonth7,dateday7))
        date_YMD7 = temporary_date_YMD7[0:10]
        seventhdateweekday_int=seventhdate.isoweekday()
        seventhdateweekday_str=week_day_dict[seventhdateweekday_int]  # list2 firstweeklist_weekday

    firstweeklist=[date_YMD,date_YMD2,date_YMD3,date_YMD4,date_YMD5,date_YMD6,date_YMD7]
    firstweeklist_weekday=[firstdateweekday_str,seconddateweekday_str,thirddateweekday_str,fourthdateweekday_str,fifthdateweekday_str,sixthdateweekday_str,seventhdateweekday_str]
    if request.method == 'POST':
        #search part
        search_date_str = request.form.get('dateinput')
        # search_weekday_str = request.form.get('weekoutput')
        print(search_date_str)
        print(type(search_date_str))
        #next/last button
        lsatbutton=request.form.get('lastinstruction')
        nextbutton=request.form.get('nextinstruction')
        print(lsatbutton)
        print(nextbutton)
        currentdate_str= request.form.get('firstdaydate')   #get information from head of table (it's the current date(string) )
        print(currentdate_str)
        print(type(currentdate_str))
        currentdate_datetype = datetime.strptime(currentdate_str, "%Y-%m-%d")
        print(currentdate_datetype)
        print(type(currentdate_datetype))
        currentweekday_int=currentdate_datetype.isoweekday()
        print(currentweekday_int)
        print(type(currentweekday_int))
        currentweekday_str=week_day_dict[currentweekday_int]
        print(currentweekday_str)
        print(type(currentweekday_str))
        if nextbutton == 'next week':
            firstdate = currentdate_datetype+ dt.timedelta(days=+7)
            #datedetail = dt.datetime.strptime(str(firstdate), '%Y-%m-%d %H:%M:%S')
            dateyear = firstdate.year
            datemonth = firstdate.month
            dateday = firstdate.day
            temporary_date_YMD = str(datetime(dateyear,datemonth,dateday))
            date_YMD = temporary_date_YMD[0:10]   # list1 firstweeklist
            firstdateweekday_int=firstdate.isoweekday()
            firstdateweekday_str=week_day_dict[firstdateweekday_int]  # list2 firstweeklist_weekday
            print(firstdateweekday_int)
            print(firstdateweekday_str)

            seconddate = firstdate + dt.timedelta(days=+1)
            dateyear2 = seconddate.year
            datemonth2 = seconddate.month
            dateday2 = seconddate.day
            temporary_date_YMD2 = str(datetime(dateyear2,datemonth2,dateday2))
            date_YMD2 = temporary_date_YMD2[0:10]   # list1 firstweeklist
            seconddateweekday_int=seconddate.isoweekday()
            seconddateweekday_str=week_day_dict[seconddateweekday_int]  # list2 firstweeklist_weekday
            print(seconddateweekday_int)
            print(seconddateweekday_str)

            thirddate = firstdate + dt.timedelta(days=+2)
            dateyear3 = thirddate.year
            datemonth3 = thirddate.month
            dateday3 = thirddate.day
            temporary_date_YMD3 = str(datetime(dateyear3,datemonth3,dateday3))
            date_YMD3 = temporary_date_YMD3[0:10]    # list1 firstweeklist
            thirddateweekday_int=thirddate.isoweekday()
            thirddateweekday_str=week_day_dict[thirddateweekday_int]  # list2 firstweeklist_weekday
            print(thirddateweekday_int)
            print(thirddateweekday_str)

            fourthdate = firstdate + dt.timedelta(days=+3)
            dateyear4 = fourthdate.year
            datemonth4 = fourthdate.month
            dateday4 = fourthdate.day
            temporary_date_YMD4 = str(datetime(dateyear4,datemonth4,dateday4))
            date_YMD4 = temporary_date_YMD4[0:10]    # list1 firstweeklist
            fourthdateweekday_int=fourthdate.isoweekday()
            fourthdateweekday_str=week_day_dict[fourthdateweekday_int]  # list2 firstweeklist_weekday
            print(fourthdateweekday_int)
            print(fourthdateweekday_str)

            fifthdate = firstdate + dt.timedelta(days=+4)
            dateyear5 = fifthdate.year
            datemonth5 = fifthdate.month
            dateday5 = fifthdate.day
            temporary_date_YMD5 = str(datetime(dateyear5,datemonth5,dateday5))
            date_YMD5 = temporary_date_YMD5[0:10]    # list1 firstweeklist
            fifthdateweekday_int=fifthdate.isoweekday()
            fifthdateweekday_str=week_day_dict[fifthdateweekday_int]  # list2 firstweeklist_weekday
            print(fifthdateweekday_int)
            print(fifthdateweekday_str)

            sixthdate = firstdate + dt.timedelta(days=+5)
            dateyear6 = sixthdate.year
            datemonth6 = sixthdate.month
            dateday6 = sixthdate.day
            temporary_date_YMD6 = str(datetime(dateyear6,datemonth6,dateday6))
            date_YMD6 = temporary_date_YMD6[0:10]    # list1 firstweeklist
            print(sixthdate)    # for test
            sixthdateweekday_int=sixthdate.isoweekday()
            print(sixthdateweekday_int)   # for test
            sixthdateweekday_str=week_day_dict[sixthdateweekday_int]  # list2 firstweeklist_weekday
            print(sixthdateweekday_int)
            print(sixthdateweekday_str)

            seventhdate = firstdate + dt.timedelta(days=+6)
            dateyear7 = seventhdate.year
            datemonth7 = seventhdate.month
            dateday7 = seventhdate.day
            temporary_date_YMD7 = str(datetime(dateyear7,datemonth7,dateday7))
            date_YMD7 = temporary_date_YMD7[0:10]    # list1 firstweeklist
            seventhdateweekday_int=seventhdate.isoweekday()
            seventhdateweekday_str=week_day_dict[seventhdateweekday_int]  # list2 firstweeklist_weekday
            print(seventhdateweekday_int)
            print(seventhdateweekday_str)

            firstweeklist=[date_YMD,date_YMD2,date_YMD3,date_YMD4,date_YMD5,date_YMD6,date_YMD7]
            firstweeklist_weekday=[firstdateweekday_str,seconddateweekday_str,thirddateweekday_str,fourthdateweekday_str,fifthdateweekday_str,sixthdateweekday_str,seventhdateweekday_str]
            return render_template('public_class_manager.html', firstlist=firstweeklist, firstlist_weekday=firstweeklist_weekday, class_basic_result=class_basic_select, class_detail_information=class_detail_selected,day8=date_YMD,day9=date_YMD2, day10=date_YMD3, day11=date_YMD4,day12=date_YMD5, day13=date_YMD6,day14=date_YMD7,date=datetime.now(),usertype = session['usertype'], name = session['name'])  #
        
        elif lsatbutton == 'last week':
            firstdate = currentdate_datetype+ dt.timedelta(days=-7)
            #datedetail = dt.datetime.strptime(str(firstdate), '%Y-%m-%d %H:%M:%S')
            dateyear = firstdate.year
            datemonth = firstdate.month
            dateday = firstdate.day
            temporary_date_YMD = str(datetime(dateyear,datemonth,dateday))
            date_YMD = temporary_date_YMD[0:10]   # list1 firstweeklist
            firstdateweekday_int=firstdate.isoweekday()
            firstdateweekday_str=week_day_dict[firstdateweekday_int]  # list2 firstweeklist_weekday

            seconddate = firstdate + dt.timedelta(days=+1)
            dateyear2 = seconddate.year
            datemonth2 = seconddate.month
            dateday2 = seconddate.day
            temporary_date_YMD2 = str(datetime(dateyear2,datemonth2,dateday2))
            date_YMD2 = temporary_date_YMD2[0:10]   # list1 firstweeklist
            seconddateweekday_int=seconddate.isoweekday()
            seconddateweekday_str=week_day_dict[seconddateweekday_int]  # list2 firstweeklist_weekday

            thirddate = firstdate + dt.timedelta(days=+2)
            dateyear3 = thirddate.year
            datemonth3 = thirddate.month
            dateday3 = thirddate.day
            temporary_date_YMD3 = str(datetime(dateyear3,datemonth3,dateday3))
            date_YMD3 = temporary_date_YMD3[0:10]    # list1 firstweeklist
            thirddateweekday_int=thirddate.isoweekday()
            thirddateweekday_str=week_day_dict[thirddateweekday_int]  # list2 firstweeklist_weekday

            fourthdate = firstdate + dt.timedelta(days=+3)
            dateyear4 = fourthdate.year
            datemonth4 = fourthdate.month
            dateday4 = fourthdate.day
            temporary_date_YMD4 = str(datetime(dateyear4,datemonth4,dateday4))
            date_YMD4 = temporary_date_YMD4[0:10]    # list1 firstweeklist
            fourthdateweekday_int=fourthdate.isoweekday()
            fourthdateweekday_str=week_day_dict[fourthdateweekday_int]  # list2 firstweeklist_weekday

            fifthdate = firstdate + dt.timedelta(days=+4)
            dateyear5 = fifthdate.year
            datemonth5 = fifthdate.month
            dateday5 = fifthdate.day
            temporary_date_YMD5 = str(datetime(dateyear5,datemonth5,dateday5))
            date_YMD5 = temporary_date_YMD5[0:10]    # list1 firstweeklist
            fifthdateweekday_int=fifthdate.isoweekday()
            fifthdateweekday_str=week_day_dict[fifthdateweekday_int]  # list2 firstweeklist_weekday

            sixthdate = firstdate + dt.timedelta(days=+5)
            dateyear6 = sixthdate.year
            datemonth6 = sixthdate.month
            dateday6 = sixthdate.day
            temporary_date_YMD6 = str(datetime(dateyear6,datemonth6,dateday6))
            date_YMD6 = temporary_date_YMD6[0:10]    # list1 firstweeklist
            sixthdateweekday_int=sixthdate.isoweekday()
            sixthdateweekday_str=week_day_dict[sixthdateweekday_int]  # list2 firstweeklist_weekday

            seventhdate = firstdate + dt.timedelta(days=+6)
            dateyear7 = seventhdate.year
            datemonth7 = seventhdate.month
            dateday7 = seventhdate.day
            temporary_date_YMD7 = str(datetime(dateyear7,datemonth7,dateday7))
            date_YMD7 = temporary_date_YMD7[0:10]    # list1 firstweeklist
            seventhdateweekday_int=seventhdate.isoweekday()
            seventhdateweekday_str=week_day_dict[seventhdateweekday_int]  # list2 firstweeklist_weekday

            firstweeklist=[date_YMD,date_YMD2,date_YMD3,date_YMD4,date_YMD5,date_YMD6,date_YMD7]
            firstweeklist_weekday=[firstdateweekday_str,seconddateweekday_str,thirddateweekday_str,fourthdateweekday_str,fifthdateweekday_str,sixthdateweekday_str,seventhdateweekday_str]
            return render_template('public_class_manager.html', firstlist=firstweeklist, firstlist_weekday=firstweeklist_weekday, class_basic_result=class_basic_select, class_detail_information=class_detail_selected,day8=date_YMD,day9=date_YMD2, day10=date_YMD3, day11=date_YMD4,day12=date_YMD5, day13=date_YMD6,day14=date_YMD7,date=datetime.now(),usertype = session['usertype'], name = session['name'])  #
        
        elif search_date_str !="":
         #search date part
            search_date_date = datetime.strptime(search_date_str, "%Y-%m-%d")
            print(search_date_date) 
            """ 
            This 19 lines code below is for make the day you search directly dont't appears on the first place of a seven-days timeable.
            It will return to the Monday your searched-date located at of the week, if you don't use the 19 lines code below
            """
            selectedyear=search_date_date.year
            selectedmonth=search_date_date.month
            selectedday=search_date_date.day
            selecteddate_temporary=datetime(selectedyear,selectedmonth,selectedday)
            selecteddate_int=selecteddate_temporary.isoweekday()
            if selecteddate_int == 1:
                selecteddate_date = selecteddate_temporary
            elif selecteddate_int == 2:
                selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-1)
            elif selecteddate_int == 3:
                selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-2)    
            elif selecteddate_int == 4:
                selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-3)
            elif selecteddate_int == 5:
                selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-4)
            elif selecteddate_int == 6:
                selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-5)
            elif selecteddate_int == 7:
                selecteddate_date = selecteddate_temporary+ dt.timedelta(days=-6)

            firstdate = selecteddate_date
            #datedetail = dt.datetime.strptime(str(firstdate), '%Y-%m-%d %H:%M:%S')
            dateyear = firstdate.year
            datemonth = firstdate.month
            dateday = firstdate.day
            temporary_date_YMD = str(datetime(dateyear,datemonth,dateday))
            date_YMD = temporary_date_YMD[0:10]   # list1 firstweeklist
            firstdateweekday_int=firstdate.isoweekday()
            firstdateweekday_str=week_day_dict[firstdateweekday_int]  # list2 firstweeklist_weekday

            seconddate = firstdate + dt.timedelta(days=+1)
            dateyear2 = seconddate.year
            datemonth2 = seconddate.month
            dateday2 = seconddate.day
            temporary_date_YMD2 = str(datetime(dateyear2,datemonth2,dateday2))
            date_YMD2 = temporary_date_YMD2[0:10]   # list1 firstweeklist
            seconddateweekday_int=seconddate.isoweekday()
            seconddateweekday_str=week_day_dict[seconddateweekday_int]  # list2 firstweeklist_weekday

            thirddate = firstdate + dt.timedelta(days=+2)
            dateyear3 = thirddate.year
            datemonth3 = thirddate.month
            dateday3 = thirddate.day
            temporary_date_YMD3 = str(datetime(dateyear3,datemonth3,dateday3))
            date_YMD3 = temporary_date_YMD3[0:10]    # list1 firstweeklist
            thirddateweekday_int=thirddate.isoweekday()
            thirddateweekday_str=week_day_dict[thirddateweekday_int]  # list2 firstweeklist_weekday

            fourthdate = firstdate + dt.timedelta(days=+3)
            dateyear4 = fourthdate.year
            datemonth4 = fourthdate.month
            dateday4 = fourthdate.day
            temporary_date_YMD4 = str(datetime(dateyear4,datemonth4,dateday4))
            date_YMD4 = temporary_date_YMD4[0:10]    # list1 firstweeklist
            fourthdateweekday_int=fourthdate.isoweekday()
            fourthdateweekday_str=week_day_dict[fourthdateweekday_int]  # list2 firstweeklist_weekday

            fifthdate = firstdate + dt.timedelta(days=+4)
            dateyear5 = fifthdate.year
            datemonth5 = fifthdate.month
            dateday5 = fifthdate.day
            temporary_date_YMD5 = str(datetime(dateyear5,datemonth5,dateday5))
            date_YMD5 = temporary_date_YMD5[0:10]    # list1 firstweeklist
            fifthdateweekday_int=fifthdate.isoweekday()
            fifthdateweekday_str=week_day_dict[fifthdateweekday_int]  # list2 firstweeklist_weekday

            sixthdate = firstdate + dt.timedelta(days=+5)
            dateyear6 = sixthdate.year
            datemonth6 = sixthdate.month
            dateday6 = sixthdate.day
            temporary_date_YMD6 = str(datetime(dateyear6,datemonth6,dateday6))
            date_YMD6 = temporary_date_YMD6[0:10]    # list1 firstweeklist
            sixthdateweekday_int=sixthdate.isoweekday()
            sixthdateweekday_str=week_day_dict[sixthdateweekday_int]  # list2 firstweeklist_weekday

            seventhdate = firstdate + dt.timedelta(days=+6)
            dateyear7 = seventhdate.year
            datemonth7 = seventhdate.month
            dateday7 = seventhdate.day
            temporary_date_YMD7 = str(datetime(dateyear7,datemonth7,dateday7))
            date_YMD7 = temporary_date_YMD7[0:10]    # list1 firstweeklist
            seventhdateweekday_int=seventhdate.isoweekday()
            seventhdateweekday_str=week_day_dict[seventhdateweekday_int]  # list2 firstweeklist_weekday

            firstweeklist=[date_YMD,date_YMD2,date_YMD3,date_YMD4,date_YMD5,date_YMD6,date_YMD7]
            firstweeklist_weekday=[firstdateweekday_str,seconddateweekday_str,thirddateweekday_str,fourthdateweekday_str,fifthdateweekday_str,sixthdateweekday_str,seventhdateweekday_str]
            return render_template('public_class_manager.html', firstlist=firstweeklist, firstlist_weekday=firstweeklist_weekday, class_basic_result=class_basic_select, class_detail_information=class_detail_selected,day8=date_YMD,day9=date_YMD2, day10=date_YMD3, day11=date_YMD4,day12=date_YMD5, day13=date_YMD6,day14=date_YMD7,date=datetime.now(),usertype = session['usertype'], name = session['name'])       
        else:
            return redirect(url_for('public_class_manager' ))
    return render_template('public_class_manager.html', firstlist=firstweeklist, firstlist_weekday=firstweeklist_weekday, class_basic_result=class_basic_select, class_detail_information=class_detail_selected,day8=date_YMD,day9=date_YMD2, day10=date_YMD3, day11=date_YMD4,day12=date_YMD5, day13=date_YMD6,day14=date_YMD7,date=datetime.now(),usertype = session['usertype'], name = session['name'])

@app.route("/add_class_interface", methods = ['GET','POST'])   # this part is for manager to add new class.
def add_class_interface():
    if request.method == 'POST':
        groupclassid_given = request.form.get('groupclassid')  ###### waiting for changing  
        print(groupclassid_given)
        print(type(groupclassid_given))    
        groupclassname_given= request.form.get('groupclassname')
        print(groupclassname_given)  
        classdate_given= request.form.get('classdate')
        print(classdate_given)
        weekoutput_given= request.form.get('weekoutput')
        print(weekoutput_given)
        classstarttime_given= request.form.get('classstarttime')
        print(classstarttime_given)
        classendtimetime_given= request.form.get('classendtime')
        print(classendtimetime_given)  
        maximumnumber_given= request.form.get('maximumnumber')
        print(maximumnumber_given)  
        location_given= request.form.get('location')
        print(location_given)  
        description_given= request.form.get('description')
        print(description_given)  
        trainerid_given= request.form.get('trainerid')
        print(trainerid_given)  

        cur = getCursor()
        cur.execute("INSERT INTO group_class values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (group_class_id) DO UPDATE SET user_id=EXCLUDED.user_id, group_class_name=EXCLUDED. group_class_name, description=EXCLUDED.description, maximum_number=EXCLUDED. maximum_number, location=EXCLUDED.location, group_class_date=EXCLUDED.group_class_date, group_class_day=EXCLUDED.group_class_day, group_class_start_time=EXCLUDED.group_class_start_time, group_class_end_time= EXCLUDED.group_class_end_time;",(int(groupclassid_given),trainerid_given,groupclassname_given,description_given,maximumnumber_given,location_given,classdate_given,weekoutput_given,classstarttime_given,classendtimetime_given,))             
        session['successs'] = True
        flash("Successfully!  You have added %s !" % (groupclassname_given,))
        return redirect(url_for('public_class_manager' ))    
    else:
        id = gen_id()
        groupclass_info = [id]
        cur = getCursor()
        cur.execute("SELECT DISTINCT user_id, first_name, last_name FROM trainer;")
        selected_trainer = cur.fetchall()  
        return render_template('add_class_interface.html', groupclass_id=groupclass_info, select_trainer=selected_trainer,date=datetime.now(),usertype = session['usertype'], name = session['name']) 

@app.route("/update_class_interface", methods = ['GET','POST'])    # this part is for manager to select which class you want to update.
def update_class_interface():
    cur = getCursor()
    cur.execute("SELECT * FROM group_class")
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    return render_template('update_class_interface.html',dbresult=select_result, dbcols=column_names, date=datetime.now(),usertype = session['usertype'], name = session['name'])

@app.route("/update_class_edit", methods = ['GET','POST'])   # this part is for manager to update class.
def update_class_edit():
    if request.method == 'POST':
        groupclassid_given1 = request.form.get('classid_update')
        groupclassname_given1= request.form.get('classname_update')    
        classdate_given1= request.form.get('date_update')
        weekoutput_given1= request.form.get('weekoutput_update')
        classstarttime_given1= request.form.get('classstarttime_update')
        classendtime_given1= request.form.get('classendtime_update')
        maximumnumber_given1= request.form.get('number_update')
        location_given1= request.form.get('location_update')
        description_given1= request.form.get('description_update')
        trainerid_given1= request.form.get('trainerid_update')
        cur = getCursor()
        cur.execute("UPDATE group_class SET user_id=%s, description=%s,maximum_number=%s,location=%s,group_class_date=%s,group_class_day=%s,group_class_start_time=%s,group_class_end_time=%s WHERE group_class_id=%s;",(trainerid_given1,description_given1,maximumnumber_given1,location_given1,classdate_given1,weekoutput_given1,classstarttime_given1,classendtime_given1,groupclassid_given1))
        session['successs'] = True
        flash('Successfully Update! You have Updated %s !' % (groupclassname_given1,))
        return redirect(url_for('public_class_manager' ))
    else:
        needtobeupdated_id = request.args.get('correspondingid')
        cur = getCursor()
        cur.execute("SELECT * FROM group_class WHERE group_class_id=%s;",(needtobeupdated_id,))
        select_result = cur.fetchall()  
        column_names = [desc[0] for desc in cur.description]
        cur.execute("SELECT user_id from trainer;")
        trainer_select_temporary = cur.fetchall()
        trainer_select = [j for i in trainer_select_temporary for j in i] 
        return render_template('update_class_edit.html',trainer_result=trainer_select,dbresult_update=select_result, dbcols_update=column_names, usertype = session['usertype'], name = session['name'])

@app.route("/class_search_update", methods = ['GET','POST'])  #this part is for searching a special recording and return to the corresponding update interface.The action is just related with the same update action above when it enter the the corresponding update interface, because the special recording table is also in same action form of the same update interface.
def class_search_update():
    if request.method == 'POST':
        searchcondition_name = request.form.get('searchbox')
        print(searchcondition_name)
        cur = getCursor()
        cur.execute("select group_class_name from group_class")
        groupname_tuplelist = cur.fetchall()
        groupname_list = [j for i in groupname_tuplelist for j in i]
        if searchcondition_name in groupname_list:
            cur.execute("SELECT * FROM group_class WHERE group_class_name=%s;",(searchcondition_name,))
            select_result1 = cur.fetchall()  
            column_names1 = [desc[0] for desc in cur.description]
            needtobeupdated_id1 = request.args.get('correspondingid')
            cur.execute("SELECT * FROM group_class WHERE group_class_id=%s;",(needtobeupdated_id1,))
            select_result_update1 = cur.fetchall()  
            column_names_update1 = [desc[0] for desc in cur.description]
            return render_template('update_class_interface.html',dbresult=select_result1, dbcols=column_names1,dbresult_update1=select_result_update1, dbcols_update1=column_names_update1,date=datetime.now(),usertype = session['usertype'], name = session['name'])
        else:
            return redirect(url_for('update_class_interface' ))

@app.route("/delete_class_interface", methods = ['GET','POST'])  # this part is the original delete interface from the delete button link.
def delete_class_interface():
    cur = getCursor()
    cur.execute("SELECT * FROM group_class")
    select_result = cur.fetchall()  
    column_names = [desc[0] for desc in cur.description]
    return render_template('delete_class_interface.html',dbresult=select_result, dbcols=column_names, date=datetime.now(),usertype = session['usertype'], name = session['name']) 
      
@app.route("/delete_action", methods = ['GET','POST'])    #this part is for the delete function action.
def delete_action():
    if request.method == 'POST':
        delete_id_fromhtml =  request.form.getlist('delete_id')
        cur = getCursor()
        cur.execute("SELECT group_class_id FROM group_booking;")
        comparied = cur.fetchall() 
        comparied_booking = [j for i in comparied for j in i]
        test(comparied_booking,'566666666666666666666')
        print(delete_id_fromhtml)
        deleteitems_length = len(delete_id_fromhtml)
        if deleteitems_length !=0:
            for delete_id_each in delete_id_fromhtml:
                test(delete_id_each,'55555555555555555555555555555555555555555555')
                if int(delete_id_each) in comparied_booking:
                    session['successs'] = True
                    flash('Sorry! You can not delete %s!' % (str(delete_id_each),))
                    return redirect(url_for('public_class_manager' )) 
                else:
                    print(delete_id_each)
                    cur = getCursor()
                    cur.execute("SELECT group_class_name FROM group_class WHERE group_class_id=%s;",(str(delete_id_each),))
                    deleted_name_list = cur.fetchall() 
                    deletedname = [j for i in deleted_name_list for j in i]
                    cur.execute("DELETE FROM group_class WHERE group_class_id=%s;",(str(delete_id_each),))
                    session['successs'] = True
                    flash('Successfully！You have deleted %s %s!' % (str(delete_id_each),deletedname[0]))
                    return redirect(url_for('public_class_manager' )) 
        else:
            return redirect(url_for('delete_class_interface' ))
            
@app.route("/delete_search", methods = ['GET','POST']) #this part is for searching a special recording and return to the corresponding delete interface.The action is just related with the same delete action above when it enter the the corresponding delete interface, because the special recording table is also in same action form of the same delete interface. 
def delete_search():
    if request.method == 'POST':
        searchcondition_name = request.form.get('searchbox')
        print(searchcondition_name)
        cur = getCursor()
        cur.execute("select group_class_name from group_class")
        groupname_tuplelist = cur.fetchall()
        groupname_list = [j for i in groupname_tuplelist for j in i]
        if searchcondition_name in groupname_list:
            cur.execute("SELECT * FROM group_class WHERE group_class_name=%s;",(searchcondition_name,))
            select_result1 = cur.fetchall()  
            column_names1 = [desc[0] for desc in cur.description]
            return render_template('delete_class_interface.html',dbresult1=select_result1, dbcols1=column_names1,date=datetime.now(),usertype = session['usertype'], name = session['name'])
        else:
            return redirect(url_for('delete_class_interface' ))

@app.route("/groupclass_report_generator", methods = ['GET','POST'])   #this part is the groupclass_report_generator interface.
def groupclass_report_generator():
    return render_template('groupclass_report_generator.html', usertype = session['usertype'], name = session['name'])

@app.route("/groupclass_report", methods = ['GET','POST'])     #this part is  for generating group class attendacne table.
def groupclass_report():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        cur = getCursor()
        cur.execute("SELECT to_char(to_date (group_class_date,'yyyy-mm-dd'),'Mon') AS class_month, sum(count)\
            FROM group_class_attendance WHERE group_class_date BETWEEN %s AND %s \
            AND group_class_name = 'BOX FIT' GROUP BY class_month;" ,(start_date,end_date),)
        boxfit_attendance = cur.fetchall()

        cur = getCursor()
        cur.execute("SELECT to_char(to_date (group_class_date,'yyyy-mm-dd'),'Mon') AS class_month, sum(count)\
            FROM group_class_attendance WHERE group_class_date BETWEEN %s AND %s \
            AND group_class_name = 'Body Combat' GROUP BY class_month;",(start_date,end_date),)
        bodycombat_attendance = cur.fetchall()

        cur = getCursor()
        cur.execute("SELECT to_char(to_date (group_class_date,'yyyy-mm-dd'),'Mon') AS class_month, sum(count)\
            FROM group_class_attendance WHERE group_class_date BETWEEN %s AND %s \
            AND group_class_name ='Grit Cardio' GROUP BY class_month;",(start_date,end_date),)
        gritcardio_attendance = cur.fetchall()

        cur = getCursor()
        cur.execute("SELECT to_char(to_date (group_class_date,'yyyy-mm-dd'),'Mon') AS class_month, sum(count)\
            FROM group_class_attendance WHERE group_class_date BETWEEN %s AND %s \
            AND group_class_name = 'Sprint'  GROUP BY class_month;" ,(start_date,end_date),)
        sprint_attendance = cur.fetchall()

        cur = getCursor()
        cur.execute("SELECT to_char(to_date (group_class_date,'yyyy-mm-dd'),'Mon') AS class_month, sum(count)\
            FROM group_class_attendance WHERE group_class_date BETWEEN %s AND %s \
            AND group_class_name = 'Yoga' GROUP BY class_month;",(start_date,end_date),)
        yoga_attendance = cur.fetchall()

        cur = getCursor()
        cur.execute("SELECT to_char(to_date (group_class_date,'yyyy-mm-dd'),'Mon') AS class_month, sum(count)\
            FROM group_class_attendance WHERE group_class_date BETWEEN %s AND %s  GROUP BY class_month;" \
            ,(start_date,end_date),)
        total_attendance = cur.fetchall()

        print(start_date)
        print(end_date)
    return render_template('groupclass_report.html', usertype = session['usertype'], \
        name = session['name'], boxfit_attendance=boxfit_attendance, bodycombat_attendance=bodycombat_attendance, \
        gritcardio_attendance=gritcardio_attendance, sprint_attendance=sprint_attendance, yoga_attendance=yoga_attendance, \
        total_attendance=total_attendance, start_date=start_date,end_date=end_date)


""" The seventh part is for manager, you can manage Personal training information. """


@app.route("/session_list", methods = ['GET','POST'])   #this part is for viewing personal class inforamtion.
def session_list():
    course = getCursor()
    if request.method == 'POST':
        start = request.form.get('start')
        end = request.form.get('end')
        sql = "SELECT pt_class.*, trainer.first_name, trainer.last_name \
        FROM pt_class LEFT JOIN trainer on pt_class.user_id = trainer.user_id WHERE \
        pt_class.pt_class_date between '%s' AND '%s' ORDER BY pt_class.pt_class_date;" %(start,end)
        course.execute(sql)
        pt_list = course.fetchall()
        cust_time = [start,end]
    else:
        delete_id = request.args.get('delete_id')
        if delete_id:
            sql = "DELETE FROM pt_class WHERE pt_class_id = %s;" % int(delete_id)
            course.execute(sql)
            flash('The session has been deleted!')
        sql = "select pt_class.*, trainer.first_name, trainer.last_name \
        from pt_class LEFT JOIN trainer on pt_class.user_id = trainer.user_id where \
        pt_class.pt_class_date >= current_date order by pt_class.pt_class_date;"
        course.execute(sql)
        pt_list = course.fetchall()
        test(pt_list,'pppppppppppppppppppppppppppppppppppppppppppp')
        cust_time = False
    return render_template('session_list.html',usertype = session['usertype'], 
    name = session['name'], pt_list = pt_list, cust = cust_time)

@app.route("/session_edit", methods = ['GET','POST'])  #this part is for editing personal class inforamtion.
def session_edit():
    course = getCursor()
    if request.method == 'POST':
        inputs = request.form
        weeklist = ['Monday', 'Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        week_n = datetime.strptime(inputs['date'],"%Y-%m-%d").weekday()
        weekday = weeklist[week_n]
        sql = "INSERT INTO pt_class values (%s,%s,'%s', '%s', %s, '%s')ON CONFLICT \
                (pt_class_id) DO UPDATE SET user_id = EXCLUDED.user_id , pt_class_date = EXCLUDED.pt_class_date ,\
                pt_class_time = EXCLUDED.pt_class_time , pt_class_cost = EXCLUDED.pt_class_cost , pt_class_day = \
                EXCLUDED.pt_class_day; " % (int(inputs['id']), int(inputs['trainerid']),inputs['date'],
                inputs['time'],float(inputs['cost']), weekday)
        test(weekday,'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        course.execute(sql)
        flash ("The session has been updated!")
        return redirect('/session_list')
    else:
        update_id = request.args.get('update_id')
        if update_id:
            test(update_id,'ppppppppppppppppppppppppppppppp')
            sql = "SELECT pt_class.*, trainer.first_name, trainer.last_name FROM pt_class \
                INNER JOIN trainer ON pt_class.user_id = trainer.user_id WHERE pt_class_id = %s" % int(update_id)
            course.execute(sql)
            pt_info = course.fetchone()
        else:
            id = gen_id()
            pt_info = [id]
        course.execute("SELECT DISTINCT user_id, first_name, last_name FROM trainer;")
        trainer_list = course.fetchall()
        test(trainer_list,'tttttttttttttttttttttttttttttttttttttttt')
    return render_template('session_edit.html', pt_info = pt_info, trainer_list = trainer_list,usertype = session['usertype'], 
    name = session['name'])

@app.route("/attendance_review/pt", methods = ['GET','POST'])  #this part is  for generating personal class attendacne table.
def attendance_pt():
    course = getCursor()
    sql = "select count(pt_class_date),trainerid, first_name, last_name from pt_attendance \
            where pt_class_date BETWEEN(NOW()- INTERVAL '1 months') AND now() group by trainerid,\
            first_name, last_name order by trainerid ;" 
    course.execute(sql)   
    period_attend = course.fetchall()
    selected = False
    customised = False
    cust_time = False
    if request.method == 'POST':
        period = request.form.get('period')
        start = request.form.get('start')
        end = request.form.get('end')
        if period:
            sql = "select count(pt_class_date),trainerid, first_name, last_name from pt_attendance \
                where pt_class_date BETWEEN(NOW()- INTERVAL '%s months') AND now() group by trainerid,\
                first_name, last_name order by trainerid ;" % int(period)
            course.execute(sql)   
            period_attend = course.fetchall()
            
            selected = period
            test(period_attend ,'pppppppppppppppppppppppppppppppp')
        else:
            test(start,'ssssssssssssssssssssssss')
            test(end,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            sql = "select count(pt_class_date),trainerid, first_name, last_name from pt_attendance \
                where pt_class_date BETWEEN '%s' AND '%s' group by trainerid,\
                first_name, last_name order by trainerid ;" %(start, end)
            course.execute(sql)
            customised = course.fetchall()
            
            cust_time =[start,end]

    return render_template('attendance_pt.html',usertype = session['usertype'], 
    name = session['name'], selected = selected , period_attend = period_attend,
    cust = customised,cust_time = cust_time)


""" The eighth part is for manager, you can watch your gym financial information. """


@app.route("/financial_report_generator", methods = ['GET','POST'])  #this part is the financial_report_generator interface.
def financial_report_generator():
    return render_template('financial_report_generator.html', usertype = session['usertype'], name = session['name'])

@app.route("/financial_report", methods = ['GET','POST'])   #this part is  for generating financial report attendacne table.
def financial_report():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        cur = getCursor()
        cur.execute("SELECT to_char(payment_date, 'Mon') as month, sum(paid_amount) \
        from membership_payments WHERE payment_date BETWEEN %s AND %s group by month;" \
            ,(start_date,end_date),)
        membership_payments = cur.fetchall()

        cur = getCursor()
        cur.execute("SELECT to_char(payment_date, 'Mon') as month, sum(paid_amount) \
        from pt_payments WHERE payment_date BETWEEN %s AND %s group by month;" \
            ,(start_date,end_date),)
        pt_payments = cur.fetchall()

        cur = getCursor()
        cur.execute("SELECT to_char(payment_date, 'Mon') as month, sum(paid_amount) \
        from total_payments WHERE payment_date BETWEEN %s AND %s group by month;" \
            ,(start_date,end_date),)
        total_payments = cur.fetchall()

        print(start_date)
        print(end_date)
    return render_template('financial_report.html', usertype = session['usertype'], \
        name = session['name'], membership_payments=membership_payments, pt_payments=pt_payments, \
        total_payments=total_payments, start_date=start_date,end_date=end_date)


""" The neineth part is for trainer, you can view and manage your own basic information, class information and your class attendance. """


@app.route("/trainer/")  #This part is the first interface for trainer.
def trainer():
    trainerid = session['userid']
    cursor = getCursor()
    sql = "SELECT * FROM trainer WHERE user_id = %s;" % trainerid
    cursor.execute(sql)
    trainerinfo = cursor.fetchone()
    return render_template( 'management_trainer.html',usertype = session['usertype'], 
    name = session['name'], info=trainerinfo)

@app.route("/profile",methods=['GET', 'POST'])   # this part is used by both member and trainer part, you as a trainer and member ,you can view your basic information
def profile():
    viewer = False
    attendance = False
    cursor = getCursor()
    trainerid = request.args.get('trainerid')
    memberid = request.args.get('memberid')
    usertype = session['usertype']
    if trainerid:
        sql = 'SELECT * FROM trainer WHERE user_id = %s;' % trainerid
        viewer = 'member'
    elif memberid:
        sql = "SELECT pt_class_date FROM booked_pt WHERE user_id = %s AND attendance_status = 'present';"% memberid
        cursor.execute(sql)
        pt_attend = cursor.fetchall()
        sql = "SELECT group_class_date FROM booked_group WHERE user_id = %s AND attendance_status = 'present';"% memberid
        cursor.execute(sql)
        group_attend = cursor.fetchall()
        sql = "SELECT gym_attendance_date FROM attendance WHERE user_id = %s AND attendance_status = 'present';"% memberid
        cursor.execute(sql)
        total_attend = cursor.fetchall()
        m3 = ['3m', attend_times(total_attend, 90),attend_times(group_attend, 90),attend_times(pt_attend, 90)]
        m6 = ['6m',attend_times(total_attend, 180),attend_times(group_attend, 180),attend_times(pt_attend, 180)]
        y1 = ['1y',attend_times(total_attend, 365),attend_times(group_attend, 365),attend_times(pt_attend, 365)]
        total = ['all', attend_times(total_attend, 9999),attend_times(group_attend, 9999),attend_times(pt_attend, 9999)]
        attendance = [m6,y1,total,m3]
        sql = "SELECT * FROM member WHERE user_id = %s;" % memberid
        viewer = 'trainer'
    else:
        userid = session['userid']
        sql = "SELECT * FROM %s WHERE user_id = %s;" % (usertype, userid)
    cursor.execute(sql)
    profileinfo = cursor.fetchone()
    return render_template('profile_view.html', profileinfo = profileinfo, 
    usertype = usertype, viewer = viewer, trainerid = trainerid, name = session['name'], 
    attendance = attendance)

@app.route("/profile/edit",methods=['GET', 'POST'])  # this part is used by both member and trainer part, you as a trainer and member ,you can edit your basic information
def profile_edit():
    userid = session['userid']
    usertype = session['usertype']
    memberid = request.args.get('memberid')
    viewer = False
    cursor = getCursor()
    if request.method == 'POST':
        form = request.form
        email = form['email'].strip().lower() 
        if form['edit'] == 'member':
            sql = "INSERT INTO member values (%s,'%s','%s', '%s', '%s', '%s','%s','%s','%s','%s','%s')ON CONFLICT \
                (user_id) DO UPDATE SET first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name,\
                phone_number = EXCLUDED.phone_number, email_address = EXCLUDED.email_address, address = \
                EXCLUDED.address,date_of_birth = EXCLUDED.date_of_birth, gender= EXCLUDED.gender,  goals \
                = EXCLUDED.goals, medical_notes = EXCLUDED.medical_notes,photo_url = EXCLUDED.photo_url"\
                % (int(form['memberid']), (form['firstname']),form['lastname'],form['phone'],email,
                 form['address'], form['birthday'], form['gender'], form['goals'],form['medical'],form['photo'])
        elif usertype == 'trainer':
            sql = sql = "INSERT INTO trainer values (%s,'%s','%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s')ON CONFLICT \
                (user_id) DO UPDATE SET first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name,\
                phone_number = EXCLUDED.phone_number, email_address = EXCLUDED.email_address, address = \
                EXCLUDED.address,date_of_birth = EXCLUDED.date_of_birth, gender= EXCLUDED.gender,  specialty \
                = EXCLUDED.specialty, years_of_experience = EXCLUDED.years_of_experience,certification = \
                EXCLUDED.certification, photo_url = EXCLUDED.photo_url" % (int(form['memberid']), (form['firstname']),
                form['lastname'],form['phone'],email, form['address'], form['birthday'], form['gender'],
                form['speciality'],form['experience'],form['certification'],form['photo'])

        cursor.execute(sql)
        if usertype =='manager' and form['edit'] == 'member':
            flash ("The member's personal information has been updated")
            return redirect(url_for('member_list'))
        elif usertype =='manager' and form['edit'] == 'trainer':
            flash ("The trainer's personal information has been updated")
            return redirect(url_for('member_list')) ###############
        else:
            flash ('Your personal information has been updated')
            return redirect(url_for('profile'))
    else:
        if memberid:
            sql = "SELECT * FROM member WHERE user_id = %s;"% (memberid)
            viewer = 'edit_member'
        else:
            sql = "SELECT * FROM %s WHERE user_id = %s;" % (usertype, userid)
        cursor.execute(sql)
        profileinfo = cursor.fetchone()
        return render_template('profile_edit.html', profileinfo = profileinfo, 
        usertype = usertype, name = session['name'],viewer = viewer )

@app.route("/trainer/followed_members", methods=['GET', 'POST'])  # this part is for trainer to follow their members' booked information 
def followed_members():
    trainerid = session['userid']
    cursor = getCursor()
    sql = "SELECT distinct booked_pt.user_id, member.first_name, member.last_name FROM \
        booked_pt inner join member on booked_pt.user_id = member.user_id where \
            booked_pt.trainerid = %s;" % trainerid
    cursor.execute(sql)
    pt_members = cursor.fetchall()
    
    sql = "select group_class_id,group_class_name, group_class_date, group_class_day, \
        group_class_start_time, count(attendance_status) as attend_member, count(user_id)\
        as booked_member from booked_group  where trainer_id = %s group by group_class_id, \
        group_class_name,group_class_date, group_class_day, group_class_start_time ORDER BY \
        group_class_date DESC;" % trainerid
    cursor.execute(sql)
    groups= cursor.fetchall()
    group_classlist = []
    now = time.time()  
    for item in groups:
        class_time = time.strptime(f'{item[2]} {item[4]}',"%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(class_time)
        if now > timestamp:
            group_classlist.append(item)

    return render_template('followed_members.html', pt_members = pt_members, 
            usertype = session['usertype'], classlist = group_classlist, name = session['name'])


""" The tenth part is for member, you can view and manage your own basic information, 
class information and check in your class. You also can view class information and pay 
for what you want"""


@app.route("/member",methods=['GET','POST'])    #This is member's first interface, there is no profile part for member, because member's profile is used by both trainer and member.
def member():
    userid = session['userid']
    cursor = getCursor()
    sql = "SELECT member.*, membership.* FROM member INNER JOIN membership ON member.user_id = \
        membership.user_id WHERE member.user_id = %s; " % userid
    cursor.execute(sql)
    memberinfo = cursor.fetchone()
    cursor.execute("SELECT * FROM booked_group WHERE user_id = %s AND booking_status = \
        'booked' AND to_date(group_class_date, 'yyyy-mm-dd') = current_date;",(userid,)) 

    groups = cursor.fetchall()  
    now = time.time()  
    booked_groups = []
    for item in groups:
        class_time = time.strptime(f'{item[8]} {item[10]}',"%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(class_time)
        if now < timestamp:
            booked_groups.append(item)
    cursor.execute("select * from booked_pt WHERE user_id= %s AND pt_class_date = \
            current_date AND (booking_status = 'payed' OR booking_status IS null);",(userid,))   
    pts = cursor.fetchall()  
    booked_pts = []
    for item in pts:
        start_time = dt.datetime.strptime(f'{item[7]} {item[8]}',"%Y-%m-%d %H:%M:%S")
        end_time = start_time + dt.timedelta(hours=1)
        timestamp = time.mktime(end_time.timetuple())
        if now < timestamp:
            booked_pts.append(item)
    test(booked_pts,'111111111111111111111111111111111111111111111111')
    if request.method == 'POST':
        group_bookingids = request.form.getlist('group_bookingid')
        pt_bookingids = request.form.getlist('pt_bookingid')
        date = session['date']
        sql = "INSERT INTO attendance values (%s, '%s', 'present');"%(userid,date)
        cursor.execute(sql)
        if group_bookingids:
            for bookingid in group_bookingids:
                sql ="UPDATE group_booking SET attendance_status = 'present' \
                    WHERE group_booking_id = %s" % int(bookingid)
                cursor.execute(sql)
        if pt_bookingids:
            for bookingid in pt_bookingids:
                sql ="UPDATE pt_booking SET attendance_status = 'present' \
                    WHERE pt_booking_id = %s" % int(bookingid)
                cursor.execute(sql)
    return render_template( 'management_member.html',usertype = session['usertype'], 
    name = session['name'], memberinfo = memberinfo, booked_groups = booked_groups, 
    booked_pts = booked_pts )

@app.route("/trainer_introduction", methods = ['POST','GET'])   # this part is for member to view trainer's basic information and select which member want.
def trainer_introduction():
    userid = session['userid']
    cursor = getCursor()
    cursor.execute("SELECT * FROM trainer ORDER BY first_name;")
    trainer_info = cursor.fetchall()
    if request.method == 'POST':
        content = request.form.get('name')
        content_f = strip(content)
        names = []
        for item in trainer_info:
            trainer_name =strip( f'{item[1]}{item[2]}')
            if content_f in trainer_name:
                cursor.execute("SELECT * FROM trainer WHERE user_id = %s;",(item[0],))
                trainer_info = cursor.fetchall()
            else:
                names.append(trainer_name)
        if len(names) == len(trainer_info):
            flash (f'No record of Trainer {content}, please check your input!')
            return redirect(url_for('trainer_introduction'))


            
    return render_template( 'trainer_introduction.html',trainer_info = trainer_info, 
    usertype = session['usertype'], name = session['name'] )

@app.route("/book_group_class/", methods=['GET'])    # this part is for member to book  public class.
def book_group_class():
    # Pick up the member's user id number
    userid = session['userid']
    print(userid)
    
    # Checks whether the member is already booked the class 
    cur =getCursor()

    cur.execute("SELECT group_class_id FROM group_booking WHERE user_id= %s AND \
        booking_status='booked' AND cancel_date IS NULL", \
         (int(userid),))
    booked_classes_id = cur.fetchall()

    confirmed_booked_classes_id = []
    for booked_class in booked_classes_id:
        for class_id in booked_class:
            confirmed_booked_classes_id.append(class_id)
    print(confirmed_booked_classes_id)
    
    # Checks whether there are spaces available or fully booked 
    
    cur.execute("SELECT group_class_id FROM group_class_booking_count WHERE count >30;")
    fully_booked_classes = cur.fetchall()

    fully_booked_classes_id =[]
    for fully_booked in fully_booked_classes:
        for class_id in fully_booked:
            fully_booked_classes_id.append(class_id)
    print(fully_booked_classes_id)

    yesterday = datetime.now() - timedelta(days=1)
    next_seven_days = datetime.now() + timedelta(days=6)
    print(yesterday)
    print(next_seven_days)

    # Displays the list of group classes available to be booked 
    # Product Owner wants this displayed as a calendar timetable - STILL IN PROCESS
    cur = getCursor()
    cur.execute("SELECT * FROM group_classes_view WHERE to_date BETWEEN %s and %s;",(yesterday,next_seven_days,))
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")

    return render_template('book_group_class.html',dbresult=select_result,dbcols=column_names, 
        confirmed_booked_classes_id=confirmed_booked_classes_id, 
        fully_booked_classes_id=fully_booked_classes_id, 
        usertype = session['usertype'], name = session['name'])

@app.route("/book_group_class/confirmation", methods=['GET','POST'])  # this part is for member to confirm public class.
def book_group_class_confirmation():
    if request.method == 'POST':
        userid = session['userid']
        
        group_class_id = request.form.get('group_class_id')
        booking_date = date.today()
        booking_status = request.form.get('booking_status')
        print(userid)
        print(group_class_id)
        print(booking_date)
        print(booking_status)

        # Insert the booking to the database
        cur = getCursor()
        cur.execute("INSERT INTO group_booking(group_class_id, user_id, booking_date, booking_status) \
            VALUES (%s,%s,%s,%s);",(int(group_class_id),userid,booking_date,booking_status,))
        return redirect("/booked_class")
    else:
        group_class_id = request.args.get('group_class_id')
        print(group_class_id)
        
        # Displays the details of the group class booking
        cur = getCursor()
        cur.execute("SELECT group_class.group_class_id, group_class.group_class_day, \
            group_class.group_class_date, group_class.group_class_start_time, group_class.group_class_end_time, \
            group_class.group_class_name, group_class.location, trainer.first_name AS trainer, \
            trainer.last_name FROM group_class JOIN trainer ON trainer.user_id = group_class.user_id \
            WHERE group_class.group_class_id=%s;",(int(group_class_id),))
        select_result = cur.fetchone()
        column_names = [desc[0] for desc in cur.description]
        print(f"{column_names}")

        return render_template('book_group_class_confirmation.html',result=select_result, \
            usertype = session['usertype'], name = session['name'])

@app.route("/pt_booking", methods=['GET', 'POST'])   # this part is for member to book  personal class.
def pt_booking():
    userid = session['userid']
    date = session['date']
    cursor = getCursor()
    if request.method == 'POST':
        ptids = request.form.getlist('ptid')

        for ptid in ptids:
            id = gen_id()
            sql = "INSERT INTO pt_booking values(%s, %s, %s,'%s', 'pending', null, null);" % (id, int(ptid), userid,date)
            cursor.execute(sql)

        return redirect(url_for('payment'))
    else:
        trainerid = int(request.args.get('trainerid'))
        sql = "SELECT *, EXTRACT (MONTH from pt_class_date) AS pt_month FROM pt_class \
            WHERE user_id = %s AND pt_class_date >= current_date\
            ORDER BY pt_class_date, pt_class_time;" % trainerid
        cursor.execute(sql)
        pt_info = cursor.fetchall()
        cursor.execute("SELECT pt_class_id FROM pt_booking WHERE booking_status = 'payed';")
        booked = cursor.fetchall()
        
        booked_ids = []
        for item in booked:
            booked_ids.append(item[0])
        
        

        return render_template( 'personal_training.html', ptinfos = pt_info, 
        booked = booked_ids,usertype = session['usertype'], name = session['name'])

@app.route("/payment", methods = ['POST','GET'])   # this part is for member to pay for  personal class.
def payment():
    cursor = getCursor()
    userid = session['userid']
    date = session['date']
    sql = "SELECT * FROM booked_pt  WHERE booking_status = 'pending' AND user_id = %s" % userid
    cursor.execute(sql)
    payinfos = cursor.fetchall()
    if request.method == 'POST':
        cancel = request.form.get('cancel')
        print(cancel, type(cancel), 'cccccccccccccccccccccccccccccccccccc')
        if cancel == 'cancel':
            for payinfo in payinfos:
                sql = "DELETE FROM pt_booking WHERE pt_booking_id =%s;" % payinfo[0]
                cursor.execute(sql)
            return redirect(url_for('trainer_introduction'))

        else:
            for payinfo in payinfos:
                id = gen_id()
                pt_id = str(payinfo[0])
                amount = request.form.get(pt_id)

                print(payinfo[0],type(payinfo[0]),'6666666666666666666666666666666666666')
                sql = "UPDATE pt_booking SET booking_status = 'payed', booking_date \
                    = '%s' where pt_booking_id = %s;" % (date, payinfo[0])
                cursor.execute(sql)
                sql = "INSERT INTO pt_payment VALUES(%s,%s,'%s',%s);" %(id, payinfo[0], date, float(amount))
                cursor.execute(sql)
            flash ('Personal Sessions successfully booked!')
            return redirect(url_for('booked_class'))
    else:
        units = len(payinfos)
        amount =float(units* 50) 
        
        return render_template( 'payment.html',usertype = session['usertype'], 
        name = session['name'], units = units,amount = amount, payinfos = payinfos)

@app.route("/refund", methods=['GET', 'POST'])
def refund():
    cursor = getCursor()
    date = str(dt.datetime.today())
    if request.method == 'POST':
        infos = request.form.getlist('amount')
        for item in infos:
            pt_id = item.split()[0]
            pt_amount = float(item.split()[1])
            refund_id = gen_id()
            sql = "INSERT INTO pt_refund values (%s, %s,'%s', %s);"% (refund_id, pt_id, date,pt_amount)
            cursor.execute(sql)
            sql = "UPDATE pt_booking SET booking_status = 'canceled', cancel_date = '%s' \
                WHERE pt_booking_id = %s" % (date, pt_id)
            cursor.execute(sql)

        flash ('Your classes have been canceled!')
            

    return redirect(url_for('booked_class'))

@app.route("/booked_class", methods = ['GET', 'POST']) # this part is for member to view their own booked class.
def booked_class():
    userid = session['userid']
    date = str(dt.datetime.today())
    cursor = getCursor()
    if request.method == 'POST':
        groupids = request.form.getlist('group_bookingid')
        ptids = request.form.getlist('pt_bookingid')

        print(ptids,'7888888888888888888888888888888888')
        if groupids:
            for groupid in groupids:



                cursor.execute("UPDATE group_booking SET booking_status = 'canceled', \
                cancel_date = %s WHERE group_booking_id = %s; ", (date, groupid))
        if ptids:
            now_date = dt.datetime.now()
            now = time.mktime(time.strptime("2021-03-19 00:00:00","%Y-%m-%d %H:%M:%S")) 
            full_refunds = []
            half_refunds = []
            no_refunds = []

            test(ptids,'4444444444444444444444444444444444444444')
            for ptid in ptids:
                sql = "SELECT * FROM booked_pt where pt_booking_id = %s;" % int(ptid)
                cursor.execute(sql)
                pt = cursor.fetchone()
                test(pt,'4444444444444444444444444444444444444444')
                pt_list = list(pt)
                pt_time = dt.datetime.strptime(f'{pt[7]} {pt[8]}',"%Y-%m-%d %H:%M:%S")
                one_day = pt_time -  dt.timedelta(hours= 24)
                pt_stamp = time.mktime(pt_time.timetuple())
                one_day_stamp = time.mktime(one_day.timetuple())

                if now < one_day_stamp:
                    pt_list.append(float(pt[12])*1)
                    full_refunds.append(pt_list )
                elif one_day_stamp< now < pt_stamp:
                    pt_list.append(float(pt[12])*0.9)
                    half_refunds.append(pt_list)
                elif pt_stamp < now:
                    pt_list.append(0.0)
                    no_refunds.append(pt_list)
            return render_template('refund.html', full_refunds = full_refunds, 
                half_refunds = half_refunds,no_refunds = no_refunds, usertype = session['usertype'], 
                name = session['name'])
        flash ('Your classes have been canceled!')
        return redirect(url_for('booked_class'))
    else:
        cursor = getCursor()

        cursor.execute("SELECT * FROM booked_group WHERE user_id = %s AND \
            (booking_status != 'canceled' OR booking_status IS  NULL) ORDER BY to_date\
            (group_class_date, 'yyyy-mm-dd') DESC;",(userid,)) 
        groups = cursor.fetchall()  
        now = time.time()  
        booked_groups = []
        for item in groups:
            class_time = time.strptime(f'{item[8]} {item[10]}',"%Y-%m-%d %H:%M:%S")
            timestamp = time.mktime(class_time)
            if now < timestamp:
                booked_groups.append(item)
        column_names1 = [desc[0] for desc in cursor.description]
        cursor.execute("select * from booked_pt WHERE user_id= %s AND pt_class_date >= \
            current_date AND (booking_status = 'payed' OR booking_status IS null);",(userid,))
        booked_pts = cursor.fetchall()  
        
        test(booked_pts,'6666666666666666666666666666666666')
    return render_template('booked_information.html', usertype = session['usertype'],
    booked_groups = booked_groups, booked_pts = booked_pts, name = session['name'])

@app.route("/payment_information", methods = ['GET','POST'])  # this part is for member to view their own payment and membership information.
def payment_information():
    memberid = session['userid']
    cur = getCursor()
    cur.execute("select first_name from member where user_id=%s",(memberid,))
    membername = cur.fetchall()
    membername_select = [j for i in membername for j in i]
    Firstname = membername_select[0]
    """ This part is for everything about payment date below"""
    cur = getCursor()
    cur.execute("select membership_type from membership where user_id=%s",(memberid,))
    membershiptype = cur.fetchall()

    membershiptype_select = [j for i in membershiptype for j in i]
    membershiptype_result = membershiptype_select[0]   ### convert list into str
    print(membershiptype_result)
    cur.execute("select payment_date from membership_payment where user_id=%s \
        order by payment_date DESC limit 1;" ,(memberid,))
    paydate = str(cur.fetchone()[0])

    cur.execute("select membership_dueday from membership where user_id=%s",(memberid,))
    lastduedate = cur.fetchall()
    lastduedate_select = [j for i in lastduedate for j in i]
    lastduedate_string = str(lastduedate_select[0])
    datedetail = dt.datetime.strptime(str(lastduedate_select[0]), '%Y-%m-%d')
    dateyear = datedetail.year
    datemonth = datedetail.month
    dateday = datedetail.day
    lastduedate_datetime = datetime(dateyear,datemonth,dateday)
    remained_detail_temporary = lastduedate_datetime - datetime.now()  
    if lastduedate_datetime >= datetime.now():                      
        remained_detail = remained_detail_temporary                 
    else:                                                            
        remained_detail = "0 day"           
    print(remained_detail)
    print(type(remained_detail))
    cur.execute("select balance, outstanding_amount from membership WHERE user_id=%s",(memberid,))
    payment_info = cur.fetchone()

    return render_template('payment_information.html',Member_id_display = memberid, 
    name_display = Firstname, 
    lastdate = paydate, payment_info = payment_info,
    membershiptype_result=membershiptype_select[0], 
    duedate=lastduedate_string[0:12], remained_day = str(remained_detail)[0:9],  
    date=datetime.now(),usertype = session['usertype'], name = session['name'])

@app.route("/membershippay", methods = ['GET','POST'])  # # this part is for member to pay for their membership.
def membershippay():
    memberid_given = session['userid']
    cur = getCursor()
    sql ="SELECT membership.*, membership_type.membership_type_cost FROM membership \
        LEFT JOIN membership_type on membership.membership_type = membership_type.membership_type \
        where user_id=%s" % memberid_given
    cur.execute(sql)
    membership = cur.fetchone()
    membershiptype_database = membership[1]
    memberunitcost_database = membership[8]
    outstanding_balance_original = membership[7]
    balance_original = membership[6]
    cur.execute("select payment_date from membership_payment where user_id=%s order \
        by payment_date DESC limit 1;",(memberid_given,))
    lastpaydate_select = cur.fetchall()
    lastpaydate_select_list = [j for i in lastpaydate_select for j in i]
    lastpaydate_database = lastpaydate_select_list[0]
    print(lastpaydate_database)

    if request.method == 'POST':
        membershiptype_given = request.form.get('membershiptypes')
        unitcost_given = request.form.get('unitcost')
        print(unitcost_given)
        print(type(unitcost_given))
        quantity_given = request.form.get('quantity')
        print(quantity_given)
        print(type(quantity_given))
        Amount_given = request.form.get('Amount')
        payment_date_given = datetime.now()

        if membershiptype_given == "weekly":
            calculate_week = int(quantity_given) * 7
            due_date_given = lastpaydate_database + timedelta(calculate_week)  ##
        elif membershiptype_given == "monthly":
            due_date_given = lastpaydate_database + relativedelta(months=int(quantity_given)) #+ timedelta(days=-ms_quantity)
        elif membershiptype_given == "yearly":   #####
            due_date_given = lastpaydate_database + relativedelta(years=int(quantity_given)) #+ timedelta(days=-ms_quantity)

        calculation = float(Amount_given)-float(unitcost_given)*int(quantity_given)
        calculation_op = float(unitcost_given)*int(quantity_given) - float(Amount_given)
        if calculation > 0:
            if outstanding_balance_original > calculation:
                outstanding_result = outstanding_balance_original - calculation
                balance_result = 0
            elif outstanding_balance_original < calculation:
                outstanding_result = 0
                balance_result = calculation - outstanding_balance_original
            elif outstanding_balance_original == calculation:
                outstanding_result = 0
                balance_result = balance_original + calculation
        elif calculation < 0:
            if balance_original > calculation_op:
                outstanding_result = 0
                balance_result = balance_original - calculation_op
            elif balance_original < calculation_op:
                outstanding_result = calculation_op - balance_original
                balance_result = 0
        elif calculation == 0:
            outstanding_result = outstanding_balance_original
            balance_result = balance_original
        
        cur = getCursor()
        id = gen_id()
        cur.execute("UPDATE membership SET outstanding_amount = %s, balance = %s, \
            membership_dueday = %s WHERE user_id = %s", (outstanding_result, balance_result,
            due_date_given,memberid_given,))
        cur.execute("INSERT INTO membership_payment VALUES(%s,%s,%s,%s,%s);\
            ", (id, memberid_given, payment_date_given,quantity_given,Amount_given,))
        session['successs'] = True
        flash("Successfully! %s You have been a formal member!" % (memberid_given,))
        return redirect('/payment_information')
    return render_template('membershippay.html', membershiptype_result=membershiptype_database,
    memberunitcost_result=memberunitcost_database, lastpaydate_result=lastpaydate_database, 
    date=datetime.now(),usertype = session['usertype'], name = session['name'])


if __name__ == '__main__':
    app.run(debug=True)
