import datetime
from datetime import datetime as dt

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as opy
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# Create your views here.
from django.views.generic import TemplateView
from mktdata.forms import DateRangeForm
from mktdata.models import Dukaeurusdtick


########################################################################################################################
# Public View Methods
########################################################################################################################
@login_required
def dashboard(request):
    return render(request, 'mktdata/dashboard.html', {'section': 'dashboard'})


# @login_required
# def data(request):
#     return render(request, 'mktdata/data.html', {'section': 'dashboard'})


class MktData(LoginRequiredMixin, TemplateView):
    """
    This Template View Class displays a graph of data with some input controls
    """
    template_name = "mktdata/data.html"

    def get_context_data(self, **kwargs):
        context = super(MktData, self).get_context_data(**kwargs)

        timestamp = Dukaeurusdtick.objects.values_list('bid', flat=True)[:1000]
        timestamp = list(timestamp)

        x = np.array(range(1, 1000))
        y = np.array(timestamp)
        trace1 = go.Scatter(x=x, y=y, marker={'color': 'red', 'symbol': 104, 'size': "10"},
                            mode="lines", name='1st Trace')

        data = go.Data([trace1])
        layout = go.Layout(title="Data", xaxis={'title': 'x1'}, yaxis={'title': 'x2'})
        figure = go.Figure(data=data, layout=layout)
        div = opy.plot(figure, auto_open=False, output_type='div')

        context['graph'] = div

        return context


def render_eurusd_mktdata(request):
    """
    View function to render a graph of eurusd mkt data
    If the request method is a POST then get start and end dates from the request object
    otherwise compute the start/end dates from the latest data in the DB
    """

    end_date = Dukaeurusdtick.objects.values_list('timestamp', flat=True).last() - datetime.timedelta(2)
    last_date_with_data = end_date;
    start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    show_volume = True
    time_frame = 'Tick'

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            start_date_date = cd["start_date"]
            start_date_dt = dt.strptime(start_date_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
            start_date = pytz.timezone('utc').localize(start_date_dt)
            end_date_date = cd["end_date"]
            end_date_dt = dt.combine(end_date_date, dt.max.time())
            end_date = pytz.timezone('utc').localize(end_date_dt)
            show_volume = cd["show_volume"]
            time_frame = cd["time_frame"]

    date_range_form = DateRangeForm(
        {'start_date': start_date, 'end_date': end_date, 'show_volume': show_volume, 'time_frame': time_frame})

    graph_data = get_graph_data(start_date, end_date, show_volume, time_frame);

    return render(request, "mktdata/data.html", {'form': date_range_form,
                                                 'graph': graph_data,
                                                 'start_date': start_date,
                                                 'end_date': end_date,
                                                 'last_date_with_data': last_date_with_data})


########################################################################################################################
# Private Methods
########################################################################################################################
def get_graph_data(startdate, enddate, show_volume, time_frame):
    """
    Given a start and end date create a plot.ly graph object from the Dukaeurusdtick data
    :param startdate: the start date to get eurusd data from
    :param enddate: the end date to get eurusd data from
    :param show_volume: boolean, represents whether to include the volume data in the plot or not
    :param time_frame: the timeframe which to show the data in (Tick, 1Sec, 3Sec, 10Sec)
    :return: a plot.ly graph object
    """

    # timestamp = Dukaeurusdtick.objects.values_list('bid', flat=True)[:1000]
    data = Dukaeurusdtick.objects.values('timestamp', 'bid', 'ask', 'bid_volume', 'ask_volume').filter(timestamp__range=(startdate, enddate))
    if len(data) < 1:
        return None

    df = pd.DataFrame.from_records(data, index='timestamp')

    if time_frame == 'Tick':
        # do nothing. data already in ticks
        data_bid = df.rename(columns={'bid': 'open'})
        data_volume = df['bid_volume']
    elif time_frame == '1Sec':
        data_bid = df['bid'].resample('1S').ohlc()
        data_volume = df['bid_volume'].resample('1S').sum()
    elif time_frame == '3Sec':
        data_bid = df['bid'].resample('3S').ohlc()
        data_volume = df['bid_volume'].resample('3S').sum()
    elif time_frame == '10Sec':
        data_bid = df['bid'].resample('10S').ohlc()
        data_volume = df['bid_volume'].resample('10S').sum()
    elif time_frame == '1Min':
        data_bid = df['bid'].resample('1Min').ohlc()
        data_volume = df['bid_volume'].resample('1Min').sum()
    elif time_frame == '5Min':
        data_bid = df['bid'].resample('5Min').ohlc()
        data_volume = df['bid_volume'].resample('5Min').sum()
    elif time_frame == '10Min':
        data_bid = df['bid'].resample('10Min').ohlc()
        data_volume = df['bid_volume'].resample('10Min').sum()
    elif time_frame == '15Min':
        data_bid = df['bid'].resample('15Min').ohlc()
        data_volume = df['bid_volume'].resample('15Min').sum()
    elif time_frame == '30Min':
        data_bid = df['bid'].resample('30Min').ohlc()
        data_volume = df['bid_volume'].resample('30Min').sum()
    elif time_frame == '1H':
        data_bid = df['bid'].resample('1H').ohlc()
        data_volume = df['bid_volume'].resample('1H').sum()
    else:
        data_bid = df['bid'].resample('1Min').ohlc()
        data_volume = df['bid_volume'].resample('1Min').sum()

    tradePrice = go.Scatter(y=data_bid["open"], x=data_bid.index, mode="lines", name='Rate')
    if show_volume:
        tradeVol = go.Bar(y=data_volume, x=data_volume.index, name='Volume', yaxis='y2', opacity=0.7)
        data = go.Data([tradePrice, tradeVol])
        layout = go.Layout(title="EURUSD Data ({})".format(time_frame),
                           xaxis=dict(title='Time'),
                           yaxis=dict(title='Rate',
                                      titlefont=dict(
                                          color='#1f77b4'
                                      ),
                                      tickfont=dict(
                                          color='#1f77b4'
                                      ),
                                      ),
                           yaxis2=dict(
                               title='Volume',
                               titlefont=dict(
                                   color='#f87f0e'
                               ),
                               tickfont=dict(
                                   color='#f87f0e'
                               ),
                               anchor='x',
                               overlaying='y',
                               side='right'
                           ),
                           )
    else:
        data = go.Data([tradePrice])
        layout = go.Layout(title="EURUSD Data ({})".format(time_frame),
                           xaxis=dict(title='Time'),
                           yaxis=dict(title='Rate',
                                      titlefont=dict(
                                          color='#1f77b4'
                                      ),
                                      tickfont=dict(
                                          color='#1f77b4'
                                      ),
                                      ),
                           )
    figure = go.Figure(data=data, layout=layout)
    graph = opy.plot(figure, auto_open=False, output_type='div')
    return graph
