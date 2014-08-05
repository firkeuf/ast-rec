# -*- coding: utf-8 -*-
from __future__ import division
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
import os
import datetime
from django.utils import timezone
from django.db.models import Q
from models import Cdr
from forms import SearchForm


def filter_from_form(form):
    """
    IN: Form
    :rtype : Queryset
    """
    src_f = Q(src__icontains=form.cleaned_data['src'])
    dst_f = Q(dst__icontains=form.cleaned_data['dst'])
    time_f = Q(calldate__gte=form.cleaned_data['start_time'], calldate__lte=form.cleaned_data['end_time'])
    channel_f = Q()
    for channel in form.cleaned_data['channel']:
        channel_f |= Q(channel__icontains=channel)
    direction_f = Q(dcontext__icontains=form.cleaned_data['direction'])
    disposition_f = Q()
    for disposition in form.cleaned_data['disposition']:
        disposition_f |= Q(disposition=disposition)
    result_filter = Cdr.objects.using('asterisk_db'). \
        filter(src_f & dst_f). \
        filter(time_f). \
        filter(channel_f). \
        filter(direction_f). \
        filter(disposition_f)
    return result_filter


@login_required(login_url='/login')
def call_list_view(request):
    def calls_duration(calls):
        """
        IN: Queryset
        :rtype : dict of {sum calls min:, sum calls sec:, number of calls:}
        """
        c_d = 0
        for call in calls:
            c_d += call.billsec
        return {'min': c_d // 60, 'sec': c_d % 60, 'count': len(calls)}
    page = request.GET.get('page')
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            request.session['search_form'] = form.cleaned_data
            request.session['call_list'] = filter_from_form(form)
            page = 1
    else:
        if request.GET == {} and request.POST == {}:
            try:
                request.session.pop('search_form')
                request.session.pop('call_list')
            except KeyError:
                pass
        if 'search_form' in request.session:
            form = SearchForm(request.session['search_form'])
        else:
            form = SearchForm()
        if not 'order_by' in request.session:
            request.session['order_by'] = '-calldate'
        if 'order' in request.GET:
            if request.GET['order'] == '-calldate' or request.GET['order'] == 'calldate':
                request.session['order_by'] = request.GET['order']
        if not 'call_list' in request.session:
            request.session['call_list'] = Cdr.objects.using('asterisk_db').filter(calldate__gte=datetime.date.today())

    paginator = Paginator(request.session['call_list'].order_by(request.session['order_by']), 25)  # 25 calls per page

    try:
        p_call_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        p_call_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        p_call_list = paginator.page(paginator.num_pages)

    context = {'call_list': p_call_list,
               'total_calls_duration': calls_duration(request.session['call_list']),
               'page_calls_duration': calls_duration(p_call_list),
               'form': form,
               'module': 'call_list',
               'saved_form': request.session,
               'order_by': request.session['order_by'],
               }
    return render(request, 'ast_rec/call_list.html', context)


@login_required(login_url='/login')
def synchronous_calls(request):
    def get_synchronous_calls(calls):
        """
        IN: Queryset
        :rtype : list of [(datetime in unix, number of simultaneous calls), (...)]
        """
        count_dict = {}
        for call in calls:
            for time in (call.calldate + timezone.timedelta(seconds=i) for i in range(call.duration + 2)):
                if time.strftime('%s') in count_dict:
                    count_dict[time.strftime('%s')] += 1
                else:
                    count_dict[time.strftime('%s')] = 1
                if time == call.calldate + timezone.timedelta(seconds=call.duration + 1):
                    count_dict[time.strftime('%s')] -= 1
                elif time == call.calldate:
                    count_dict[time.strftime('%s')] -= 1

        count_l = list(count_dict.items())
        count_l.sort(key=lambda item: item[0])
        tmp_l = [count_l[i] for i in range(len(count_l) - 1) if
                 count_l[i][1] == count_l[i + 1][1] and count_l[i][1] == count_l[i - 1][1] and i > 0]
        for item in tmp_l:
            count_l.remove(item)
        return count_l

    def get_calls_by_hour(calls):
        """
        IN: Queryset
        :rtype : list of [(datetime in unix, number of simultaneous calls), (...)]
        """
        count_dict = {}
        for call in calls:
            time = datetime.datetime.strptime(call.calldate.strftime("%Y %m %d %H"), "%Y %m %d %H").strftime("%s")
            if time in count_dict:
                count_dict[time]['count'] += 1
                count_dict[time]['duration'] += call.duration
            else:
                count_dict[time] = {'count': 1, 'duration': call.duration}

        count_l = []
        duration_l = []
        for key, value in sorted(count_dict.items()):
            count_l.append((key, value['count']))
            duration_l.append((key, value['duration'] / 60))

        return {'count': count_l, 'duration': duration_l}

    if request.method == 'POST':
        form = SearchForm(request.POST)
    else:
        form = SearchForm()

    call_list = Cdr.objects.using('asterisk_db').filter(calldate__gte=datetime.date.today())

    if form.is_valid():
        call_list = filter_from_form(form)

    context = {'call_list': call_list,
               'form': form,
               'module': 'synchronous_calls',
               'saved_form': request.session,
               'synchronous_calls': get_synchronous_calls(call_list),
               'calls_by_hour': get_calls_by_hour(call_list),
    }
    return render(request, 'ast_rec/synchronous_calls.html', context)


@login_required(login_url='/login')
def by_hour_calls(request):
    def get_calls_by_hour(calls):
        """
        IN: Queryset
        :rtype : dict of {'count': [{'name': , 'label': , 'color': , 'data':[[x,y],[]...]},{}...], 'duration': [<<...]}
        """
        count_dict = {}
        duration_dict = {}
        for call in calls:
            day = call.calldate.strftime("%m.%d")
            hour = call.calldate.strftime("%H")
            if day not in count_dict:
                count_dict[day] = {}
                duration_dict[day] = {}
            if hour not in count_dict[day]:
                count_dict[day][hour] = 0
                duration_dict[day][hour] = 0
            count_dict[day][hour] += 1
            duration_dict[day][hour] += call.billsec / 60

        i = 0
        count_list = []
        duration_list = []
        colors_l = ['#0000FF', '#FF0000', '#00FFFF', '#000000', '#8A2BE2', '#A52A2A', '#DEB887', '#5F9EA0', '#D2691E',
                    '#FF7F50', "#DC143C", '#008B8B', '#B8860B', '#A9A9A9', '#006400', '#BDB76B', '#556B2F', '#FF8C00',
                    '#9932CC', '#8B0000', '#E9967A', '#8FBC8F', '#483D8B', '#2F4F4F', '#00CED1', '#FF1493', '#00BFFF',
                    '#696969', '#1E90FF', '#B22222', '#228B22', '#FF00FF', '#FFD700', '#DAA520', '#808080', '#008000',
                    '#ADFF2F', '#CC5500', '#FF69B4', '#CD5C5C', '#4B0082', '#F0E68C', '#E6E6FA', '#7CFC00', '#FFFACD',
                    '#ADD8E6', '#F08080', '#E0FFFF', '#FAFAD2', '#D3D3D3', '#90EE90', '#FFB6C1', '#FFA07A', '#20B2AA',
                    '#87CEFA', '#778899', '#B0C4DE', '#FFFFE0', '#00FF00', '#32CD32', '#FAF0E6', '#FF00FF', '#800000',
                    '#66CDAA', '#0000CD', '#BA55D3', '#9370D8', '#3CB371', '#7B68EE', '#00FA9A', '#48D1CC', '#C71585',
                    '#191970', '#F5FFFA', '#FFE4E1', '#FFE4B5', '#FFDEAD', '#000080', '#FDF5E6', '#808000', '#6B8E23',
                    '#FFA500', '#FF4500', '#DA70D6', '#EEE8AA', '#98FB98', '#AFEEEE', '#D87093', '#FFEFD5', '#FFDAB9',
                    '#CD853F', '#FFC0CB', '#DDA0DD', '#B0E0E6', '#800080', '#BC8F8F', '#4169E1', '#8B4513', '#FA8072',
                    '#F4A460', '#2E8B57', '#FFF5EE', '#A0522D', '#C0C0C0', '#87CEEB', '#6A5ACD', '#708090', '#FFFAFA',
                    '#00FF7F', '#4682B4', '#D2B48C', '#008080', '#D8BFD8', '#FF6347', '#40E0D0', '#EE82EE', '#F5DEB3',
                    '#A86363', '#F5F5F5', '#FFFF00', '#9ACD32']

        for key, value in sorted(count_dict.items()):
            calls_data = sorted(map(list, list(value.items())))
            duration_data = sorted(map(list, list(duration_dict[key].items())))

            for l in duration_data:
                l[1] = int(l[1])

            day_call = {'name': '&sum; of Calls: ', 'label': key, 'color': colors_l[i % len(colors_l)],
                        'data': calls_data}
            day_duration = {'name': '&sum; of min: ', 'label': key, 'color': colors_l[i % len(colors_l)],
                            'data': duration_data}

            count_list.append(day_call)
            duration_list.append(day_duration)
            i += 1

        return {'count': count_list, 'duration': duration_list}

    if request.method == 'POST':
        form = SearchForm(request.POST)
    else:
        form = SearchForm()
    call_list = Cdr.objects.using('asterisk_db').filter(calldate__gte=datetime.date.today())

    if form.is_valid():
        call_list = filter_from_form(form)

    context = {'form': form,
               'module': 'by_hour_calls',
               'saved_form': request.session,
               'calls_by_hour': get_calls_by_hour(call_list),
    }

    return render(request, 'ast_rec/by_hour_calls.html', context)


@login_required(login_url='/login')
@permission_required('ast_rec.can_listen', login_url='/login')
def records_xsendfile(request, uniqueid, document_root):
    path = os.path.join(document_root, uniqueid[0:3], uniqueid[0:4], uniqueid[0:5])
    filepath = os.path.join(path, uniqueid + '.mp3')
    if os.path.isfile(filepath):
        download_filename = datetime.datetime.fromtimestamp(float(uniqueid)).strftime('%Y-%m-%d_%H:%M:%S') + '.mp3'
    else:
        ls_list = os.listdir(path)
        download_filename = None
        for f in ls_list:
            if '-' + uniqueid[0:10] + '.ogg' in f:  # confbridge-1404816948.233-1404816957.ogg
                filepath = os.path.join(path, f)
                download_filename = datetime.datetime.fromtimestamp(float(uniqueid)).strftime('%Y-%m-%d_%H:%M:%S') + '.ogg'
                break

    response = HttpResponse(mimetype='application/force-download')
    response['Content-Type'] = ''
    response['Content-Disposition'] = 'attachment;filename="%s"' % download_filename
    try:
        response['Content-length'] = os.stat(filepath).st_size
    except:
        pass
    response['X-Sendfile'] = filepath.encode('utf-8')

    return response

