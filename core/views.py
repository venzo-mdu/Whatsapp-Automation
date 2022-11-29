from flask import Blueprint
from flask import jsonify,request
from datetime import date,datetime,timedelta
from pywhatkit.whats import sendwhats_image,sendwhatmsg_instantly,open_web
from . import scheduler
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

views = Blueprint('views',__name__)

# @views.route('/w',methods=['GET'])
# def whatsapp_check():
#     open_web()
# b77wc
def task(*args):
    # inputs
    client = args[0]
    file = client.open(args[1])
    today = (datetime.today()).replace(hour=0,minute=0,second=0,microsecond=0)
    # excel sheets
    details_sheet = pd.DataFrame(file.get_worksheet(0).get_all_records())
    holiday_list=(pd.DataFrame(file.get_worksheet(1).get_all_records())).to_dict('list')
    settings =  (pd.DataFrame(file.get_worksheet(2).get_all_records())).to_dict('list')
    # holidays check
    holiday_list = holiday_list['holidays']
    for i in range(0,len(holiday_list)):
        holiday_list[i] =  datetime.strptime(holiday_list[i],'%d/%m/%y')

    next_birth_days= []
    next_day = today + timedelta(days=1)
    work_day = False
    while not work_day:
        if next_day in holiday_list:
            next_birth_days.append(next_day)
            next_day += timedelta(days=1)
        else:
            work_day= True
    print(next_birth_days)
    # user details from details xl sheet
    persons = details_sheet.to_dict(orient='records')
    for person in persons:
        birth_day = person['date of birth']
        print(birth_day)
        message = None
        if isinstance(birth_day,str):
            try:
                birth_day = datetime.strptime(birth_day,'%d/%m/%Y')
            except:
                birth_day = datetime.strptime(birth_day,'%d/%m/%y')

        if birth_day.day == today.day and birth_day.month == today.month and person['status'] != 'done':
            message = person['caption']
            if person['image'] == '':
                image_path = "{}".format(settings['default image'][0])
            else:
                image_path = "{}/{}".format(settings['images folder'][0],person['image'])
        for day in next_birth_days:
            if birth_day.day == day.day and birth_day.month == day.month and person['status'] != 'done':
                message = 'advance ' + person['caption']
        # send whatsapp message
        if message:
            try:
                sendwhats_image(settings['group id'][0],image_path,message,30,20)
                print(image_path)
                print('done')
                person['status'] = 'done'
            except:
                pass
    # save changes in xl file
    df = pd.DataFrame.from_records(persons)
    change = file.get_worksheet(0)
    change.update([df.columns.values.tolist()]+df.values.tolist())


@views.route('/schedule',methods=['GET'])
def schedule_task():
    if not scheduler.state:
        scheduler.start()

    with open('./details.txt','r') as text_file:
        text = text_file.readlines()
        file_name = ((text[0].split(':'))[-1]).strip()
        file_name.replace(' ','')
        credential_json = ((text[1].split(':'))[-1]).strip()
        credential_json.replace(' ','')
    # print(file_name,'hi')
    scope_app =['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] 
    cred = ServiceAccountCredentials.from_json_keyfile_name(credential_json,scope_app) 
    client = gspread.authorize(cred)
    print(client)
    print(file_name)
    file = client.open(file_name)
    settings =  (pd.DataFrame(file.get_worksheet(2).get_all_records())).to_dict('list')
    hour = settings['time'][0][:2]
    minute = settings['time'][0][3:5]
    day_of_week = settings['schedule'][0]
    # to start scheduler
    scheduler.remove_all_jobs()
    scheduler.add_job(func=task,args=[client,file_name], trigger='cron',day_of_week=day_of_week,hour=hour,minute=minute,id='dob message')
    # return {'status':'your job was scheduled at {} everyday'.format(data['time'])}
    return {'status':'success'}
