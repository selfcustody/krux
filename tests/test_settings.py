from unittest import mock

def test_init(mocker):
    from krux.settings import Settings
    
    s = Settings()
    
    assert isinstance(s, Settings)
    
def test_store_init(mocker):
    from krux.settings import Store, SETTINGS_FILE
    
    cases = [
        (None, {}),
        ("""{"settings":{"network":"test"}}""", {'settings': {'network': 'test'}}),
    ]
    for case in cases:
        mo = mock.mock_open(read_data=case[0])
        mocker.patch('builtins.open', mo)
        s = Store()
    
        assert isinstance(s, Store)
        mo.assert_called_once_with(SETTINGS_FILE, 'r')
        assert s.settings == case[1]
    
def test_store_get(mocker):
    mo = mock.mock_open()
    mocker.patch('builtins.open', mo)
    from krux.settings import Store
    s = Store()
    
    cases = [
        ('ns1', 'setting', 'call1_defaultvalue1', 'call2_defaultvalue1'),
        ('ns1.ns2', 'setting', 'call1_defaultvalue2', 'call2_defaultvalue2'),
        ('ns1.ns2.ns3', 'setting', 'call1_defaultvalue3', 'call2_defaultvalue3'),
    ]
    for case in cases:
        # First call, setting does not exist, so default value becomes the value
        assert s.get(case[0], case[1], case[2]) == case[2]
        # Second call, setting does exist, so default value is ignored
        assert s.get(case[0], case[1], case[3]) == case[2]

def test_store_set(mocker):
    mo = mock.mock_open()
    mocker.patch('builtins.open', mo)
    from krux.settings import Store
    s = Store()
    
    cases = [
        ('ns1', 'setting', 'call1_value1', 1, 'call3_value1'),
        ('ns1.ns2', 'setting', 'call1_value2', 2, 'call3_value2'),
        ('ns1.ns2.ns3', 'setting', 'call1_value3', 3, 'call3_value3'),
    ]
    for case in cases:
        s.set(case[0], case[1], case[2])
        assert s.get(case[0], case[1], 'default') == case[2]
        
        s.set(case[0], case[1], case[3])
        assert s.get(case[0], case[1], 'default') == case[3]
        
        s.set(case[0], case[1], case[4])
        assert s.get(case[0], case[1], 'default') == case[4]

def test_setting(mocker):
    mo = mock.mock_open()
    mocker.patch('builtins.open', mo)
    from krux.settings import Setting
    
    class TestClass:
        namespace = 'test'
        some_setting = Setting('some_setting', 1)
        
    t = TestClass()
    
    assert t.some_setting == 1
    t.some_setting = 2
    assert t.some_setting == 2
