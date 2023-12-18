import datetime

from tackle import tackle


def test_provider_date_date_now():
    output = tackle('date_now.yaml')
    assert output['now'] == datetime.datetime.now().strftime("%m-%d-%Y")
    assert output['year'] == datetime.datetime.now().strftime("%Y")
    assert isinstance(output['timestamp'], float)
    assert isinstance(output['timestamp_utc'], float)
