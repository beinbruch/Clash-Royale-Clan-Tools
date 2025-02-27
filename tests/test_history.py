from crtools import history
from datetime import datetime
import copy

__fake_members__ = [
    {
        "name": "Player A",
        "tag": "#AAAAAA",
        "role": "leader",
        "donations": 100
    },
    {
        "name": "Player C",
        "tag": "#CCCCCC",
        "role": "member",
        "donations": 10
    },
    {
        "name": "Player D",
        "tag": "#DDDDDD",
        "role": "elder",
        "donations": 0
    }
]

__fake_history__ = {
    "last_update": 1549974720.0,
    "members": {
        "#AAAAAA": {
            "join_date": 1549974720.0,
            "status": "present",
            "role": "leader",
            "donations": 100,
            "events": [
                {
                    "event": "join",
                    "status": "new",
                    "role": "leader",
                    "date": 1549974720.0
                }
            ]
        },
        "#CCCCCC": {
            "join_date": 1549974720.0,
            "status": "present",
            "role": "elder",
            "donations": 5,
            "events": [
                {
                    "event": "join",
                    "status": "new",
                    "role": "elder",
                    "date": 1549974720.0
                }
            ]
        },
        "#DDDDDD": {
            "join_date": 1549974720.0,
            "status": "present",
            "role": "member",
            "donations": 5,
            "events": [
                {
                    "event": "join",
                    "status": "new",
                    "role": "member",
                    "date": 1549974720.0
                }
            ]
        },
        "#QQQQQQ": {
            "join_date": 0,
            "status": "absent",
            "role": "member",
            "events": [
                {
                    "event": "join",
                    "status": "new",
                    "role": "member",
                    "date": 0
                }
            ]
        }

    }
}

__fake_currentwar__ = {
    "state": "collectionDay",
    "participants": [
        {
            "tag": "#AAAAAA"
        }
    ]
}

def test_get_role_change_status():
    assert history.get_role_change_status('foo',                 'foo')                 == False
    assert history.get_role_change_status('foo',                 'bar')                 == False
    assert history.get_role_change_status('foo',                 history.ROLE_MEMBER)   == False
    assert history.get_role_change_status(history.ROLE_MEMBER,   'foo')                 == False
    assert history.get_role_change_status('foo',                 'foo')                 == False
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_LEADER)   == 'unchanged'
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_COLEADER) == 'demotion'
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_ELDER)    == 'demotion'
    assert history.get_role_change_status(history.ROLE_LEADER,   history.ROLE_MEMBER)   == 'demotion'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_COLEADER) == 'unchanged'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_LEADER)   == 'promotion'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_ELDER)    == 'demotion'
    assert history.get_role_change_status(history.ROLE_COLEADER, history.ROLE_MEMBER)   == 'demotion'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_ELDER)    == 'unchanged'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_LEADER)   == 'promotion'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_COLEADER) == 'promotion'
    assert history.get_role_change_status(history.ROLE_ELDER,    history.ROLE_MEMBER)   == 'demotion'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_MEMBER)   == 'unchanged'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_LEADER)   == 'promotion'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_COLEADER) == 'promotion'
    assert history.get_role_change_status(history.ROLE_MEMBER,   history.ROLE_ELDER)    == 'promotion'

def test_validate_history_new():
    timestamp = datetime.utcnow()
    new_history = {
        'last_update': timestamp,
        'members': {}
    }

    assert history.validate_history(None, timestamp) == (new_history, 0)
    assert history.validate_history("members", timestamp) == (new_history, 0)
    assert history.validate_history(False, timestamp) == (new_history, 0)
    assert history.validate_history([], timestamp) == (new_history, 0)
    assert history.validate_history({}, timestamp) == (new_history, 0)
    assert history.validate_history({'last_update':'foo'}, timestamp) == (new_history, 0)
    assert history.validate_history({'members':'foo'}, timestamp) == (new_history, 0)
    assert history.validate_history({'last_update':'foo', 'members': 'Foo'}, timestamp) == (new_history, 0)

def test_validate_history_update():
    timestamp = datetime.utcnow()
    new_history = {
        'last_update': 0,
        'members': {}
    }
    actual_history, actual_timestamp = history.validate_history(new_history, timestamp)
    assert actual_timestamp == timestamp
    assert actual_history['last_update'] == timestamp
    assert type(actual_history['members']) == dict
    assert len(actual_history['members']) == 0

def test_get_member_history_new():
    date = datetime(2019, 2, 12, 7, 32, 0, 0)
    timestamp = datetime.timestamp(date)
    h = history.get_member_history(__fake_members__, None, None, date)

    assert h['last_update'] == timestamp
    for member in __fake_members__:
        assert h['members'][member['tag']]['role'] == member['role']
        assert h['members'][member['tag']]['status'] == 'present'
        assert h['members'][member['tag']]['events'][0]['event'] == 'join'
        assert h['members'][member['tag']]['events'][0]['type'] == 'new'
        assert h['members'][member['tag']]['events'][0]['role'] == member['role']
        assert h['members'][member['tag']]['events'][0]['date'] == 0

def test_get_member_history_role_change():
    date = datetime(2019, 2, 12, 7, 32, 1, 0)
    timestamp = datetime.timestamp(date)
    h = history.get_member_history(__fake_members__, __fake_history__, None, date)

    members = h['members']

    assert h['last_update'] == timestamp
    assert members[__fake_members__[1]['tag']]['status'] == 'present'
    assert members[__fake_members__[1]['tag']]['events'][1]['event'] == 'role change'
    assert members[__fake_members__[1]['tag']]['events'][1]['type'] == 'demotion'
    assert members[__fake_members__[1]['tag']]['events'][1]['role'] == __fake_members__[1]['role']
    assert members[__fake_members__[1]['tag']]['events'][1]['date'] == timestamp

    assert members[__fake_members__[2]['tag']]['status'] == 'present'
    assert members[__fake_members__[2]['tag']]['events'][1]['event'] == 'role change'
    assert members[__fake_members__[2]['tag']]['events'][1]['type'] == 'promotion'
    assert members[__fake_members__[2]['tag']]['events'][1]['role'] == __fake_members__[2]['role']
    assert members[__fake_members__[2]['tag']]['events'][1]['date'] == timestamp

def test_get_member_history_donations_reset():
    date = datetime(2019, 2, 12, 7, 32, 1, 0)
    timestamp = datetime.timestamp(date)
    members_copy = copy.deepcopy(__fake_members__)
    members_copy[0]['donations'] = 5
    h = history.get_member_history(__fake_members__, __fake_history__, None, date)
    h2 = history.get_member_history(members_copy, h, None, date)

    members = h2['members']
    assert members[__fake_members__[0]['tag']]['donations'] == 5
    assert members[__fake_members__[0]['tag']]['donations_last_week'] == __fake_members__[0]['donations']

def test_get_member_history_unchanged():
    """ Getting history twice. Nothing should be changed except the
    timestamp """
    date = datetime(2019, 2, 12, 7, 32, 1, 0)
    date2 = datetime(2019, 2, 12, 7, 32, 2, 0)
    timestamp = datetime.timestamp(date)
    timestamp2 = datetime.timestamp(date2)

    h = history.get_member_history(__fake_members__, None, None, date)
    h2 = history.get_member_history(__fake_members__, h, None, date2)

    assert h['last_update'] == timestamp
    assert h2['last_update'] == timestamp2
    assert h['members'] == h2['members']

def test_get_member_history_quit_and_rejoin():
    date = datetime(2019, 2, 12, 7, 32, 1, 0)
    date2 = datetime(2019, 2, 12, 7, 32, 2, 0)
    timestamp = datetime.timestamp(date)
    timestamp2 = datetime.timestamp(date2)
    members = __fake_members__.copy()
    del members[2]

    h = history.get_member_history(members, __fake_history__, None, date)
    h2 = history.get_member_history(__fake_members__, h, None, date2)

    h_member = h['members'][__fake_members__[2]['tag']]
    h2_member = h2['members'][__fake_members__[2]['tag']]

    assert h_member['status'] == 'absent'
    assert h_member['events'][1]['event'] == 'quit'
    assert h_member['events'][1]['type'] == 'left'
    assert h_member['events'][1]['date'] == timestamp
    assert h2_member['status'] == 'present'
    assert h2_member['events'][1]['event'] == 'quit'
    assert h2_member['events'][1]['type'] == 'left'
    assert h2_member['events'][1]['date'] == timestamp
    assert h2_member['events'][2]['event'] == 'join'
    assert h2_member['events'][2]['type'] == 're-join'
    assert h2_member['events'][2]['date'] == timestamp2

def test_war_participation_activity_update():
    date = datetime(2019, 2, 12, 7, 32, 1, 0)
    h = history.get_member_history(__fake_members__, __fake_history__, __fake_currentwar__, date)

    h_member = h['members'][__fake_members__[0]['tag']]
    assert h_member['last_activity_date'] == datetime.timestamp(date)
