from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
import json
import numpy
import os
import re
import shutil
import stat
import time

from django.urls import reverse
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import RecInfo, RegistrationOffer

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from .computations.audio import process_audio


@login_required
def trans(request, rec_info_id):
    line_id_to_trans = get_line_id_to_trans(request)
    rec_info = RecInfo.objects.filter(id=rec_info_id)[0]
    sorted_lines = json.loads(rec_info.description)
    line_second_ends = []
    if not (line_id_to_trans is None):
        for line in sorted_lines:
            line_id = line["line_id"]
            line["trans"] = line_id_to_trans[line_id]
        rec_info.description = json.dumps(sorted_lines)
        rec_info.save()
    for line in sorted_lines:
        line_second_ends.append(line["end_sec"])
        line["human_timestamp"] = time.strftime("%H:%M:%S", time.gmtime(line["start_sec"]))
    media_url_part = media if (media := settings.MEDIA_URL) else "/"
    audio_url = "http://" + get_host(request, settings.REC_PORT) + f"{media_url_part}{rec_info.name}"
    return render(request, 'trans/trans.html', {"lines" : sorted_lines, "line_second_ends" : line_second_ends, "audio_url" : audio_url, "rec_info_id" : rec_info_id })


@login_required
def get_line_id_to_trans(request):
    # !!! TODO tie with template name
    trans_prefix = "line-trans-"
    trans_keys = [ key for key in request.POST.keys() if re.match(trans_prefix, key) ]
    if len(trans_keys) == 0:
        return None
    line_id_to_trans = {}
    for trans_key in trans_keys:
        line_id = int(re.sub(trans_prefix, "", trans_key))
        line_id_to_trans[line_id] = request.POST[trans_key]
    return line_id_to_trans
    

@login_required
def add_recording(request):
    rec_file_key = "recfile"
    split_secs_key = "splitSecondsNumber"
    template_data = {}
    if rec_file_key in request.FILES:
        temp_file = request.FILES[rec_file_key]
        out_dp = settings.REC_ROOT_DP
        out_rec_name = get_out_rec_name(temp_file.name, out_dp)
        out_fp = os.path.join(out_dp, out_rec_name)
        save_file(temp_file, out_fp)
        os.chmod(out_fp, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        const_split_seconds = None
        if split_secs_key in request.POST and request.POST[split_secs_key].strip() != "":
            const_split_seconds = int(request.POST[split_secs_key])
        split_second_timestamps = process_audio(out_fp, const_split_seconds=const_split_seconds)
        RecInfo(name=out_rec_name, description=json.dumps(get_lines(split_second_timestamps))).save()
        template_data["message"] = f"recording added with name {out_rec_name}"
    return render(request, 'trans/addrec.html', template_data)


@login_required
def list_recordings(request):
    template_infos = []
    for rec_info in RecInfo.objects.all():
        template_infos.append({ "name" : rec_info.name, "id" : rec_info.id })
    return render(request, 'trans/listrec.html', { "rec_infos" : template_infos })
    
@login_required
def get_trans_text(request, rec_info_id):
    description = RecInfo.objects.filter(id=rec_info_id)[0].description
    trans_lines = []
    for line in json.loads(description):
        trans_lines.append(line["trans"])
    return HttpResponse("\n".join(trans_lines), content_type="text/plain")


@login_required
def registration_invitation(request):
    if not request.user.has_perm("trans.add_registrationoffer"):
        return HttpResponseForbidden()
    template_data = {}
    if "email" in request.POST:
        token = get_random_string(length=32)
        RegistrationOffer(token=token).save()
        registration_url = f"{request.scheme}://{request.get_host()}{reverse('register')}?token={token}"
        send_mail(
            'TransHelp registration link',
            f'use {registration_url} to register',
            settings.EMAIL_FROM,
            [request.POST["email"]],
            fail_silently=False,
        )
        template_data["message"] = f"the following registration link has been sent {registration_url}"
    return render(request, 'trans/reginvitation.html', template_data)
    

def clean_fname(fname):
    return re.sub("[^\w.-]", "_", fname)

def get_lines(split_second_timestamps):
    curr_start = 0.
    lines = []
    for line_pos, curr_end in enumerate(split_second_timestamps):
        lines.append({ "line_id" : line_pos, "trans" : "", "start_sec" : curr_start, "end_sec" : curr_end })
        curr_start = curr_end
    return lines

def get_out_rec_name(fname, out_dp):
    clean_rec_fname = clean_fname(fname)
    out_rec_fp = os.path.join(out_dp, clean_rec_fname)
    if not os.path.exists(out_rec_fp):
        return clean_rec_fname
    for i in range(20):
        spl = re.split("\.", clean_rec_fname)
        prefix = ".".join(spl[:-1])
        out_rec_name = f"{prefix}_{i:03d}.{spl[-1]}"
        if not os.path.exists(os.path.join(out_dp, out_rec_name)):
            return out_rec_name
    raise Exception("too many files with the same name")

def save_file(temp_file, out_fp):
    if type(temp_file) is TemporaryUploadedFile:
        temp_file_fp = temp_file.temporary_file_path()
        shutil.copy(temp_file_fp, out_fp)
    elif type(temp_file) is InMemoryUploadedFile:
        with open(out_fp, "wb") as f:
            f.write(temp_file.read())
    else:
        raise ValueError(f"unknown file object type {type(temp_file)}")

def get_host(request, port):
    return re.sub(":[0-9]+$", "", request.get_host()) + f":{port}"










