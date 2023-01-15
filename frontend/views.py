from django.shortcuts import render
from background_task import background
import numpy as np
import cv2
from zipfile import ZipFile
from django.utils.timezone import now
from pathlib import Path   
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import time
import os
from datetime import date
from json.decoder import JSONDecodeError
from django.http import JsonResponse
from background_task.models import Task
from background_task.models import CompletedTask

from django.conf import settings
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from .models import Submission, Contact
import pydicom as dicom
import pydicom.uid
import PIL # optional
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from requests.structures import CaseInsensitiveDict

proxies = {
  "http": "http://proxy.cs.ui.ac.id:8080",
  "https": "http://proxy.cs.ui.ac.id:8080"
}

# BASE_URL_XRAY = "http://103.133.56.145:8003"
BASE_URL_XRAY = "http://127.0.0.1:8003"
BASE_URL_CTSCAN = "http://127.0.0.1:19900"

def home(request):
    jml_backlog = Task.objects.all().count()
    jml_done = CompletedTask.objects.all().count()
    param = {
        'jml_backlog': jml_backlog,
        'jml_done': jml_done,
        'jml_total': jml_backlog + jml_done
    }
    return render(request, 'home.html', param)


def team(request):
    jml_backlog = Task.objects.all().count()
    jml_done = CompletedTask.objects.all().count()
    param = {
        'jml_backlog': jml_backlog,
        'jml_done': jml_done,
        'jml_total': jml_backlog + jml_done
    }
    return render(request, 'team.html', param)


@csrf_exempt
def submit_contact(request):
    param = {}
    if request.method == 'POST':
        contact = Contact(
            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message'],
        )
        contact.save()
    return HttpResponse("OK")

def contact(request):
    param = {}
    return render(request, 'contact.html', param)


def upload(request):
    print(request.FILES['fileInput'])

    direktori_ymd = date.today().strftime('%Y/%m/%d/')


    print(settings.MEDIA_ROOT + "/" + direktori_ymd)
    print(settings.THUMBNAIL_ROOT + "/" + direktori_ymd)

    timestamp = int(time.time()*1000.0)
    if request.method == 'POST' and request.FILES['fileInput']:
        fileInput = request.FILES['fileInput']
        fs = FileSystemStorage()

        if not os.path.exists(settings.MEDIA_ROOT + "/" + direktori_ymd):
            os.makedirs(settings.MEDIA_ROOT + "/" + direktori_ymd)

        if not os.path.exists(settings.THUMBNAIL_ROOT + "/" + direktori_ymd):
            os.makedirs(settings.THUMBNAIL_ROOT + "/" + direktori_ymd)

        stat = 0
        filename = ""
        extension = os.path.splitext(fileInput.name)[1][1:].strip() 
        if fileInput.name.lower().endswith('.jpg') or fileInput.name.lower().endswith('.png'):
            filename = fs.save(direktori_ymd + str(timestamp) + "." + extension, fileInput)
            stat = 1
            image = Image.open(settings.MEDIA_ROOT + "/" + filename)
            MAX_SIZE = (100, 100)
            image.thumbnail(MAX_SIZE)
            image.save(settings.THUMBNAIL_ROOT + "/" + filename )

        elif fileInput.name.lower().endswith('.zip'):
            dst_file = direktori_ymd + str(timestamp) + "." + extension


            # open_lungs = select_open_lungs(str(timestamp), fileInput)
            # print(open_lungs)
            filename = fs.save(dst_file, fileInput)
            # print(filename_dcm)
            # ds = dicom.dcmread(fileInput, force=True)
            # ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
            # plt.imshow( ds.pixel_array)
            # filename = dst_file + ".png"
            # print(settings.MEDIA_ROOT)
            # plt.savefig(settings.MEDIA_ROOT + "/" + filename)
            stat = 1

        print(fs)
        print(filename)

        arg = {'stat': stat, 'file_location': filename}
        return JsonResponse(arg, safe=False)

    arg = {'stat': '0'}
    return JsonResponse(arg, safe=False)


def select_open_lungs(timestamp, file_name):
    selected_imgs = {}

    zero=[]
    names=[]
    zip_files = ZipFile(file_name, 'r')
    for i, name in enumerate(zip_files.namelist()):
        print("Proses: " + name)
        if name.endswith('/') and not os.path.exists(settings.THUMBNAIL_ROOT + "/" + timestamp + "/" + name):
            os.makedirs(settings.MEDIA_ROOT + "/" + timestamp + "/" + name)
        if name.endswith('.dcm'):
            img = zip_files.extract(name)
            dcm_file = dicom.dcmread(img)
            dcm_im = dcm_file.pixel_array
            plt.imshow( dcm_im)
            filename = name + ".png"
            print(settings.MEDIA_ROOT)
            tmp_file_dir = settings.MEDIA_ROOT + "/" + timestamp + "/" + filename

            plt.savefig(tmp_file_dir)
            dcm_uint16 = dcm_im.astype(np.uint16)
            dcm_resized = cv2.resize(dcm_uint16, dsize=(512, 512))
            names.append(i)
            sp = dcm_resized[240:340,120:370] #Crop the region
            counted_zero=0
            for i in np.reshape(sp,(sp.shape[0]*sp.shape[1],1)):
                if i<300: #count the number of pixel values in the region less than 300
                    counted_zero+=1
            zero.append(counted_zero) #add the number of dark pixels of the image to the list
    min_zero=min(zero)
    max_zero=max(zero)
    threshold=(max_zero-min_zero)/1.5 #Set the threshold
    indices=np.where(np.array(zero)>threshold) #Find the images that have more dark pixels in the region than the calculated threshold
    selected_names=np.array(names)[indices] #Selected images
    
    for i, name in enumerate(zip_files.namelist()):
        if i in selected_names:
            img = zip_files.extract(name)
            dcm_file = dicom.dcmread(img)
            dcm_im = dcm_file.pixel_array
            dcm_uint16 = dcm_im.astype(np.uint16)
            dcm_resized = cv2.resize(dcm_uint16, dsize=(512, 512))
            selected_imgs[name] = dcm_resized
    
    open_lungs_out = {}
    open_lungs_out["num_all_imgs"] = len(names)
    open_lungs_out["num_selected_imgs"] = len(selected_names)
    open_lungs_out["imgs_array"] = selected_imgs
    
    return open_lungs_out


def submit_xray(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/admin/login/", request.path))

    return redirect('/my_submission?tipe=xray')

def submit_ctscan(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/admin/login/", request.path))

    return redirect('/my_submission?tipe=ctscan')

def my_submission(request):
    if not request.user.is_authenticated:
        print(request)
        return redirect('%s?next=%s' % ("/admin/login/", request.path))

    param = {}
    return render(request, 'my_submission.html', param)

def my_submissions(request):
    if not request.user.is_authenticated:
        print(request)
        return redirect('%s?next=%s' % ("/admin/login/", request.path))

    all_my_submissions = Submission.objects.filter(author=request.user).order_by("-ts_submission")
    param = {
        'all_my_submissions': all_my_submissions
    }
    # for submission in all_my_submissions:
    #     print(submission)
        # param['all_my_submissions'].append(tmp)

    print(param)
    return render(request, 'my_submissions.html', param)


def api_insert_update_submission(request):
    if not request.user.is_authenticated or request.method != 'POST':
        arg = {'stat': '0', 'msg': 'Need to be authenticated / using POST method'}
        return JsonResponse(arg, safe=False)
    
    record_id = request.POST['record_id']
    submission = None
    if record_id != '':
        submission = Submission.objects.get(id=record_id)

        patient_id=request.POST['patient_id']

        other_patient_id = Submission.objects.filter(patient_id=patient_id, author=request.user).exclude(id=record_id).values()
        print(other_patient_id)
        if len(other_patient_id) > 0:
            arg = {'stat': '0', 'msg': 'Patient ID already used'}
            return JsonResponse(arg, safe=False)


    msg = 'Edit Record Success'
    print(request.POST)
    if submission is None:
        submission = Submission(
            patient_id = request.POST['patient_id'],
            author = request.user,
            submission_type = request.POST['submission_type'],
            submission_status = 'Queued',
            sex = request.POST['sex'],
            age = request.POST['age'],
            fever_temp = request.POST['fever_temp'],
            fever_duration = request.POST['fever_duration'],
            interpretation = request.POST['interpretation'],
            comorbidities = request.POST['comorbidities'],
            file_location = request.POST['file_location'],

            cough = request.POST['symptom_cough'],
            flu = request.POST['symptom_flu'],
            sore_throat = request.POST['symptom_sore_throat'],
            shiver = request.POST['symptom_shiver'],
            headache = request.POST['symptom_headache'],
            faint = request.POST['symptom_faint'],
            hard_to_breathe = request.POST['symptom_hard_to_breathe'],
            nausea = request.POST['symptom_nausea'],
            diarrhea = request.POST['symptom_diarrhea'],
            muscleache = request.POST['symptom_muscleache'],
            abdominal_pain = request.POST['symptom_abdominal_pain'],
            other_conditions = request.POST['other_conditions'],
        )
        msg = 'Insert Record Success'
    else:
        submission.patient_id = request.POST['patient_id']
        submission.submission_type = request.POST['submission_type']
        submission.sex = request.POST['sex']
        submission.age = request.POST['age']
        submission.fever_temp = request.POST['fever_temp']
        submission.fever_duration = request.POST['fever_duration']
        submission.interpretation = request.POST['interpretation']
        submission.comorbidities = request.POST['comorbidities']
        submission.file_location = request.POST['file_location']

        submission.age = request.POST['age']
        submission.cough = request.POST['symptom_cough']
        submission.flu = request.POST['symptom_flu']
        submission.sore_throat = request.POST['symptom_sore_throat']
        submission.shiver = request.POST['symptom_shiver']
        submission.headache = request.POST['symptom_headache']
        submission.faint = request.POST['symptom_faint']
        submission.hard_to_breathe = request.POST['symptom_hard_to_breathe']
        submission.nausea = request.POST['symptom_nausea']
        submission.diarrhea = request.POST['symptom_diarrhea']
        submission.muscleache = request.POST['symptom_muscleache']
        submission.abdominal_pain = request.POST['symptom_abdominal_pain']
        submission.other_conditions = request.POST['other_conditions']
        msg = 'Edit Record Success'

    submission.save()
    proses_kalamakara(submission.id)

    arg = {'stat': '1', 'msg': msg}
    return JsonResponse(arg, safe=False)

def api_latest_submission(request):
    if 'limit' in request.GET:
        limit = int(request.GET['limit'])
        objs_my_submissions = Submission.objects.filter(author=request.user).order_by('-ts_submission')[:limit].values()
    else:
        objs_my_submissions = Submission.objects.filter(author=request.user).order_by('-ts_submission').values()

    cnt_my_submissions = Submission.objects.filter(author=request.user).count()
    latest = list(objs_my_submissions)
    arg = {'stat': '1', 'latest': latest, 'cnt_my_submissions': cnt_my_submissions}
    return JsonResponse(arg, safe=False)

def api_get_submission(request):
    record_id = request.GET['record_id']
    objs_my_submissions = Submission.objects.filter(author=request.user, id=record_id).values()

    arg = list(objs_my_submissions)
    print(arg)
    ret = {}
    if len(arg) == 1:
        ret = arg[0]

    return JsonResponse(ret, safe=False)


@background(schedule=0)
def proses_kalamakara(arg):
    print("PROCESSING ID: " + str(arg))
    submission = Submission.objects.get(id=arg)
    print(submission.submission_type)
    if submission.submission_type == 'ctscan':
        proses_ctscan(arg)
    else:
        proses_xray(arg)

def proses_ctscan(arg):
    print("OKE")

    parse_json1 = "";
    parse_json2 = "";
    parse_json3 = "";
    parse_json4 = "";
    parse_json5 = "";

    submission = Submission.objects.get(id=arg)
    submission.submission_status = 'Predicting'
    submission.save()

    print(submission.file_location)
    file_location = os.path.join(settings.MEDIA_ROOT, submission.file_location) 
    print(file_location)

    files = {'file': open(file_location, 'rb')}
    url = BASE_URL_CTSCAN + "/uploadfile/"
    print(url)
    r = requests.post(url, files=files)
    print(r.text)

    parse_json1 = json.loads(r.text)
    id_file = ""
    directory = ""
    if 'id' not in parse_json1:
        print("ID tidak ditemukan")
        if 'directory' not in parse_json1:
            print("Directory tidak ditemukan")
            return
        else:
            directory = parse_json1['directory']
    else:
        id_file = parse_json1['id']

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    kirim = 'id='+  id_file
    url = BASE_URL_CTSCAN + "/dopreproccess/"
    print(kirim)
    print("REQ: " + url)
    r = requests.post(url, headers=headers, data=kirim)
    print("RET: " + r.text)

    try:
        parse_json2 = json.loads(r.text)
    except:
        print("Parse /doprocessess/ result, error")

    
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    kirim = 'id='+  id_file
    url = BASE_URL_CTSCAN + "/doclassification/"
    print(kirim)
    print("REQ: " + url)
    r = requests.post(url, headers=headers, data=kirim)
    print("RET: " + r.text)

    try:
        parse_json3 = json.loads(r.text)
    except:
        print("Parse /doclassification/ result, error")


    headers["Content-Type"] = "application/x-www-form-urlencoded"
    kirim = 'id='+  id_file
    url = BASE_URL_CTSCAN + "/dosegmentation/"
    print(kirim)
    print("REQ: " + url)
    r = requests.post(url, headers=headers, data=kirim)
    print("RET: " + r.text)

    try:
        parse_json4 = json.loads(r.text)
    except:
        print("Parse /dosegmentation/ result, error")

    
    url = BASE_URL_CTSCAN + "/viewclassification/?directory=" + id_file
    print("REQ: " + url)
    r = requests.get(url)
    print("RET: " + r.text)

    try:
        parse_json5 = json.loads(r.text)
        print("PARSE JSON:")
        print(parse_json5)

        submission.prediction = parse_json5['predictedClass']
        submission.prob_normal = parse_json5['probability']['Normal']
        submission.prob_pneu = parse_json5['probability']['Pneumonia']
        submission.prob_covid = parse_json5['probability']['COVID']
        submission.submission_status = 'Completed'
        submission.save()

    except:
        print("Parse /viewclassification/ result, error")





    # if 'id' not in parse_json:
    #     print("ID tidak ditemukan")
    #     return

    # payload = {
    #     'interpretasi_xray': 'tidak ada',
    #     'durasi_demam': submission.fever_duration,
    #     'temperature': submission.fever_temp,
    #     'umur': submission.age,
    #     'kondisi_penyerta': submission.comorbidities,
    #     'lainnya': submission.other_conditions,
    #     'nyeri_abdomen': 'Ya' if submission.abdominal_pain else 'Tidak',
    #     'nyeri_otot': 'Ya' if submission.muscleache else 'Tidak',
    #     'sesak': 'Ya' if submission.hard_to_breathe else 'Tidak',
    #     'diare': 'Ya' if submission.diarrhea else 'Tidak',
    #     'mual': 'Ya' if submission.nausea else 'Tidak',
    #     'lemah': 'Ya' if submission.faint else 'Tidak',
    #     'sakit_kepala': 'Ya' if submission.headache else 'Tidak',
    #     'menggigil': 'Ya' if submission.shiver else 'Tidak',
    #     'sakit_tenggorokan': 'Ya' if submission.sore_throat else 'Tidak',
    #     'pilek': 'Ya' if submission.flu else 'Tidak',
    #     'batuk': 'Ya' if submission.cough else 'Tidak',
    #     'demam': 'Ya' if submission.fever_duration > 0 else 'Tidak',
    #     'jenis_kelamin': 'Laki-Laki' if submission.sex else 'Perempuan'
    # }
    # # r = requests.post(url, files=files, data=payload, proxies=proxies)

    # if r.status_code != requests.codes.ok:
    #     return False

    # submission.submission_status = 'Processing'
    # submission.save()


    # submission = Submission.objects.get(id=arg)
    # submission.submission_status = 'Predicting'
    # submission.save()

    # url = BASE_URL_CTSCAN + "/json-predict-ctscan/"
    # r = requests.get(url)
    # if r.status_code != requests.codes.ok:
    #     return False

    # parse_json = json.loads(r.text)
    # print("PARSE JSON:")
    # print(parse_json)

    # submission.prediction = parse_json['pred_class']
    # submission.prob_normal = parse_json['prob_normal']
    # submission.prob_pneu = parse_json['prob_pneu']
    # submission.prob_covid = parse_json['prob_covid']
    # submission.submission_status = 'Completed'
    # submission.save()




def proses_xray(arg):
    submission = Submission.objects.get(id=arg)
    print(submission.file_location)
    file_location = os.path.join(settings.MEDIA_ROOT, submission.file_location) 
    print(file_location)


    url = BASE_URL_XRAY + '/api/predict-xray/'
    files = {'image': open(file_location, 'rb')}
    payload = {
        'interpretasi_xray': 'tidak ada',
        'durasi_demam': submission.fever_duration,
        'temperature': submission.fever_temp,
        'umur': submission.age,
        'kondisi_penyerta': submission.comorbidities,
        'lainnya': submission.other_conditions,
        'nyeri_abdomen': 'Ya' if submission.abdominal_pain else 'Tidak',
        'nyeri_otot': 'Ya' if submission.muscleache else 'Tidak',
        'sesak': 'Ya' if submission.hard_to_breathe else 'Tidak',
        'diare': 'Ya' if submission.diarrhea else 'Tidak',
        'mual': 'Ya' if submission.nausea else 'Tidak',
        'lemah': 'Ya' if submission.faint else 'Tidak',
        'sakit_kepala': 'Ya' if submission.headache else 'Tidak',
        'menggigil': 'Ya' if submission.shiver else 'Tidak',
        'sakit_tenggorokan': 'Ya' if submission.sore_throat else 'Tidak',
        'pilek': 'Ya' if submission.flu else 'Tidak',
        'batuk': 'Ya' if submission.cough else 'Tidak',
        'demam': 'Ya' if submission.fever_duration > 0 else 'Tidak',
        'jenis_kelamin': 'Laki-Laki' if submission.sex else 'Perempuan'
    }
    # r = requests.post(url, files=files, data=payload, proxies=proxies)
    r = requests.post(url, files=files, data=payload)
    print(r.text)

    if r.status_code != requests.codes.ok:
        return False

    submission.submission_status = 'Processing'
    submission.save()

    ret = get_result(r, submission.file_location, arg)

    print("STATUS PROSES:")
    print(ret)
    if ret == False:
      submission = Submission.objects.get(id=arg)
      submission.submission_status = 'Failed'
      submission.save()
      print(submission)

    return ret

def get_result(r, server_file_location, id_record):
    url = BASE_URL_XRAY + '/api/xray-predict-result/'

    submission = Submission.objects.get(id=id_record)
    submission.submission_status = 'Predicting'
    submission.save()

    # r = requests.get(url, proxies=proxies)
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        return False

    parse_json = json.loads(r.text)
    print(parse_json)
    ret = download_anotasi(parse_json['severity'], server_file_location, id_record)

    submission = Submission.objects.get(id=id_record)
    submission.prediction = parse_json['prediction']
    submission.prob_normal = parse_json['prob_normal']
    submission.prob_pneu = parse_json['prob_pneu']
    submission.prob_covid = parse_json['prob_covid']
    submission.save()

    return ret

def download_anotasi(url_part, server_file_location, id_record):
    url = BASE_URL_XRAY + url_part
    # r = requests.get(url, proxies=proxies)
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        return False
    
    print(url)
    file_server_file_name = "result-" + Path(server_file_location).name
    file_server_subdir = os.path.dirname(server_file_location)

    dir_server_file_location = settings.MEDIA_ROOT + "/" + os.path.dirname(server_file_location)
    print("DIR: " + dir_server_file_location)
    print("FILE: " + file_server_file_name)

    image_path = dir_server_file_location + "/" + file_server_file_name
    open(image_path, 'wb').write(r.content)    

    submission = Submission.objects.get(id=id_record)
    submission.file_location_result = file_server_subdir + "/" + file_server_file_name
    submission.submission_status = 'Completed'
    submission.save()

    return True

