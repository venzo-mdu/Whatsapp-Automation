from flask import Blueprint
from flask import jsonify,request
import openpyxl
from datetime import date,datetime,timedelta
from flask_apscheduler import APScheduler
import time
from pywhatkit.whats import sendwhats_image,sendwhatmsg_instantly
from . import scheduler
import xlwt
from xlwt import Workbook
from urllib.request import urlopen,Request
import pandas



views = Blueprint('views',__name__)

# task to perform
def task(*args):
    persons = args[0]
    image_folder = args[1]
    group_id = args[2]
    file = args[3]
    book = args[4]
    birth_day_persons = []
    today = date.today()
    next_day = today + timedelta(days=1)
    max_column = file.max_column

    try:
        scheduler.remove_job('check')
    except:
        pass

    start = "{}-{}-{} 09:00:00".format(next_day.year,next_day.month,next_day.day)
    end = "{}-{}-{} 13:00:00".format(next_day.year,next_day.month,next_day.day)
    print(start,end)
    scheduler.add_job(func=task,args=[persons,image_folder,group_id,file,book],trigger='interval',hours=1,start_date=start,end_date=end,id='check')
    for i in persons:
        if isinstance(i['dob'],str):
            i['dob'] = datetime.strptime(i['dob'],'%d/%m/%Y')
        if i['dob'].day == today.day and i['dob'].month == today.month:
            birth_day_persons.append(i)


    for i in birth_day_persons:
        message = i['caption']
        image_path = "{}/{}".format(image_folder,i['image'])
        try:
            sendwhats_image(group_id,image_path,message,30,20)
            print('done')
            file.cell(i['row'],max_column,'done')
        except:
            pass
    book.save('details.xlsx')


# to start scheduler
@views.route('/schedule',methods=['POST'])
def schedule_task():
    # input data check
    data = request.json
    # start scheduler if not started
    if not scheduler.state:
        scheduler.start()

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
    # xml_book = openpyxl.load_workbook(file_path)

    # req = Request(
    #     url=file_path, 
    #     headers={'User-Agent': 'Mozilla/5.0'}
    # )
    # socket = urlopen(req)
    # xml_book = pandas.ExcelFile(socket)

    xml_book = pandas.read_excel(file_path,engine='openpyxl')
    xml_file = (xml_book).active
    first_row = list(xml_file.rows)[0]
    keys =[]
    for i in first_row:
        key = (i.value).lower()
        if 'birth' in key or 'dob' in key:
            keys.append('dob')
        else:
            keys.append(key)
    persons = []
    row_position = 1
    for row in xml_file.iter_rows(2, xml_file.max_row):
        row_position += 1
        xml_data = {}
        print(row)
        for i in range(0,len(row)):
            xml_data[keys[i]] = row[i].value
        xml_data['row'] = row_position
        persons.append(xml_data)

    if data['job'] == 'force start':
        on_time = datetime.now() + timedelta(minutes=1)
        print(on_time.hour,on_time.minute)
        scheduler.add_job(func=task,args=[persons,folder,group_id,xml_file,xml_book], trigger='date',run_date=datetime(on_time.year, on_time.month, on_time.day, on_time.hour, on_time.minute,on_time.second),id='sudden dob message')

        return {'data':"success"}

    # schedule a job

    # scheduler.remove_all_jobs()
    # scheduler.add_job(func=task,args=[persons,folder,group_id,xml_file,xml_book], trigger='cron',day_of_week='mon-sun',hour=hour,minute=minute,id='dob message')
    return {'status':'your job was scheduled at {} everyday'.format(data['time'])}


@views.route('/check',methods=['POST'])
def schedule_check():
    jobs = scheduler.get_jobs()
    print(jobs)
    return {'status': jobs}