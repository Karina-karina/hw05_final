import datetime as dt


def year(request):
    now_date = dt.datetime.now().year
    return {'year': now_date}
