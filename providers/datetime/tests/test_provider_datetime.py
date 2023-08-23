from tackle import tackle
import datetime


def test_provider_date_date_now(change_dir):
    output = tackle('date_now.yaml')
    assert output['now'] == datetime.datetime.now().strftime("%m-%d-%Y")
    assert output['year'] == datetime.datetime.now().strftime("%Y")
    assert isinstance(output['timestamp'], float)
    assert isinstance(output['timestamp_utc'], float)
