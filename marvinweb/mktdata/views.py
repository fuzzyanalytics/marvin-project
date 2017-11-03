import numpy as np
import plotly.graph_objs as go
import plotly.offline as opy
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

    end_date = Dukaeurusdtick.objects.values_list('timestamp', flat=True).last()
    start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    date_range_form = DateRangeForm()

    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            start_date = cd["start_date"]
            end_date = cd["end_date"]

    # date_range_form["start_date"] = start_date

    graph_data = get_graph_data(start_date, end_date);

    return render(request, "mktdata/data.html", {'form': date_range_form,
                                                 'graph': graph_data,
                                                 'start_date': start_date,
                                                 'end_date': end_date})


########################################################################################################################
# Private Methods
########################################################################################################################
def get_graph_data(startdate, enddate):
    """
    Given a start and end date create a plot.ly graph object from the Dukaeurusdtick data
    :param startdate: the start date to get eurusd data from
    :param enddate: the end date to get eurusd data from
    :return: a plot.ly graph object
    """

    # timestamp = Dukaeurusdtick.objects.values_list('bid', flat=True)[:1000]
    timestamp = Dukaeurusdtick.objects.values_list('bid', flat=True).filter(timestamp__range=(startdate, enddate))
    timestamp = list(timestamp)

    x = np.array(range(1, len(timestamp)))
    y = np.array(timestamp)
    trace1 = go.Scatter(x=x, y=y, marker={'color': 'red', 'symbol': 104, 'size': "10"},
                        mode="lines", name='1st Trace')

    data = go.Data([trace1])
    layout = go.Layout(title="Data", xaxis={'title': 'Date'}, yaxis={'title': 'Rate'})
    figure = go.Figure(data=data, layout=layout)
    graph = opy.plot(figure, auto_open=False, output_type='div')
    return graph
