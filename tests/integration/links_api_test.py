from datetime import datetime

import pytest


@pytest.mark.parametrize('data', [
    dict(),
    {'links': []},
    {'links1': ['ya.ru']}
])
def test_validation(client, data):
    resp = client.post(
        'api/v1/linktracker/visited_links',
        headers=[('Content-Type', 'application/json')],
        json=data
    )
    resp_data = resp.get_json()

    assert resp.status_code == 400
    assert resp_data['status'] == 'error'


@pytest.mark.parametrize('data,xmessage', [
    ({'links': ['some_text']},
     'Url "some_text" is incorrect'),

    ({'links': ['']},
     'Url is null or empty')
])
def test_url_validation(client, data, xmessage):
    resp = client.post(
        'api/v1/linktracker/visited_links',
        headers=[('Content-Type', 'application/json')],
        json=data
    )
    resp_data = resp.get_json()

    assert resp.status_code == 400
    assert resp_data['status'] == 'error'
    assert resp_data['message'] == xmessage


@pytest.mark.parametrize('from_ts,to_ts,xmessage', [
    (None, 1,
     '"from" argument is required'),

    (1, None,
     '"to" argument is required')
])
def test_timedelta_validation(client, from_ts, to_ts, xmessage):
    resp = client.get(
        'api/v1/linktracker/visited_domains',
        headers=[('Content-Type', 'application/json')],
        query_string={'from': from_ts, 'to': to_ts}
    )
    resp_data = resp.get_json()

    assert resp.status_code == 400
    assert resp_data['status'] == 'error'
    assert resp_data['message'] == xmessage


def test_visiting(client):
    data = {
        'links': [
            "https://ya.ru?q=123",
            "funbox.ru",
            "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
        ]
    }
    from_ts = datetime.now().timestamp()

    visit_resp = client.post(
        'api/v1/linktracker/visited_links',
        headers=[('Content-Type', 'application/json')],
        json=data
    )
    to_ts = datetime.now().timestamp()
    visit_resp_data = visit_resp.get_json()

    assert visit_resp.status_code == 200
    assert visit_resp_data['status'] == 'ok'

    domains_resp = client.get(
        'api/v1/linktracker/visited_domains',
        headers=[('Content-Type', 'application/json')],
        query_string={'from': from_ts, 'to': to_ts}
    )
    domains_resp_data = domains_resp.get_json()

    assert domains_resp.status_code == 200
    assert domains_resp_data['status'] == 'ok'

    found_count = 0
    for domain in domains_resp_data['domains']:
        found = False
        for link in data['links']:
            if domain in link:
                found = True
                found_count += 1
                break

        assert found

    assert found_count == len(data['links'])


def test_visiting_same_domains(client):
    from_ts = datetime.now().timestamp()
    visit_resp = client.post(
        'api/v1/linktracker/visited_links',
        headers=[('Content-Type', 'application/json')],
        json={
            'links': [
                "https://ya.ru?q=123",
                "https://ya.ru",
            ]
        }
    )
    to_ts = datetime.now().timestamp()
    visit_resp_data = visit_resp.get_json()

    assert visit_resp.status_code == 200
    assert visit_resp_data['status'] == 'ok'

    domains_resp = client.get(
        'api/v1/linktracker/visited_domains',
        headers=[('Content-Type', 'application/json')],
        query_string={'from': from_ts, 'to': to_ts}
    )
    domains_resp_data = domains_resp.get_json()

    assert domains_resp.status_code == 200
    assert domains_resp_data['status'] == 'ok'

    assert len(domains_resp_data['domains']) == 1
    assert domains_resp_data['domains'][0] == 'ya.ru'


def test_timedelta(client):
    visit_resp = client.post(
        'api/v1/linktracker/visited_links',
        headers=[('Content-Type', 'application/json')],
        json={
            'links': [
                "https://mail.ru"
            ]
        }
    )
    visit_resp_data = visit_resp.get_json()

    assert visit_resp.status_code == 200
    assert visit_resp_data['status'] == 'ok'

    from_ts = datetime.now().timestamp()
    visit_resp = client.post(
        'api/v1/linktracker/visited_links',
        headers=[('Content-Type', 'application/json')],
        json={
            'links': [
                "https://ya.ru"
            ]
        }
    )
    to_ts = datetime.now().timestamp()
    visit_resp_data = visit_resp.get_json()

    assert visit_resp.status_code == 200
    assert visit_resp_data['status'] == 'ok'

    visit_resp = client.post(
        'api/v1/linktracker/visited_links',
        headers=[('Content-Type', 'application/json')],
        json={
            'links': [
                "https://google.com"
            ]
        }
    )
    visit_resp_data = visit_resp.get_json()

    assert visit_resp.status_code == 200
    assert visit_resp_data['status'] == 'ok'

    domains_resp = client.get(
        'api/v1/linktracker/visited_domains',
        headers=[('Content-Type', 'application/json')],
        query_string={'from': from_ts, 'to': to_ts}
    )
    domains_resp_data = domains_resp.get_json()

    assert domains_resp.status_code == 200
    assert domains_resp_data['status'] == 'ok'

    assert len(domains_resp_data['domains']) == 1
    assert domains_resp_data['domains'][0] == 'ya.ru'
