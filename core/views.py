from flask import Blueprint
from flask import jsonify,request
import openpyxl
from datetime import date,datetime
from flask_apscheduler import APScheduler
import time
from pywhatkit.whats import sendwhats_image,sendwhatmsg_instantly
from . import scheduler

views = Blueprint('views',__name__)

# task to perform
def task(*args):
    persons = args[0]
    image_folder = args[1]
    group_id = args[2]
    birth_day_persons = []
    today = date.today()

    for i in persons:
        if isinstance(i['dob'],str):
            i['dob'] = datetime.strptime(i['dob'],'%d/%m/%Y')
        if i['dob'].day == today.day and i['dob'].month == today.month:
            birth_day_persons.append(i)

    print(birth_day_persons ,'hi')
    for i in birth_day_persons:
        message = i['caption']
        image_path = "{}/{}".format(image_folder,i['image'])
        sendwhats_image(group_id,image_path,message,30,20)


# to start scheduler
@views.route('/schedule',methods=['POST'])
def schedule_task():
    # input data check
    data = request.json


    if 'job' in data and data['job'] == 'stop':
        if scheduler.state:
            scheduler.shutdown()
            return {'status':'scheduled job is stopped successfully'}
        else:
            return {'status':'scheduled job is altready stopped'}

    if 'path' not in data or 'image folder' not in data or 'group id' not in data or 'time' not in data:
        return {'status':'check given details'}

    file_path = data['path']
    folder = data['image folder']
    group_id = data['group id']
    hour = data['time'][:2]
    minute = data['time'][3:5]

    # xml file to python dictionary
    xml_file = (openpyxl.load_workbook(file_path)).active
    first_row = list(xml_file.rows)[0]
    keys =[]
    for i in first_row:
        key = (i.value).lower()
        if 'birth' in key or 'dob' in key:
            keys.append('dob')
        else:
            keys.append(key)
    persons = []
    for row in xml_file.iter_rows(2, xml_file.max_row):
        xml_data = {}
        for i in range(0,len(row)):
            xml_data[keys[i]] = row[i].value
        persons.append(xml_data)

    # schedule a job
    scheduler.remove_all_jobs()
    scheduler.add_job(func=task,args=[persons,folder,group_id], trigger='cron',day_of_week='mon-sun',hour=hour,minute=minute,id='dob message')
    # start scheduler if not started
    if not scheduler.state:
        scheduler.start()
    return {'status':'your job was scheduled at {} everyday'.format(data['time'])}
