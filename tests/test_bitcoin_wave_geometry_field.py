from sce.research.bitcoin_wave_geometry import daily_wave_states


def test_wave_states_join_cells_to_timeline_in_order():
    field={"timeline":[{"time":"t1"},{"time":"t2"}],"cells":[
        {"time":"t1","scale":"1d","trend":1,"momentum":1},
        {"time":"t1","scale":"1w","trend":1,"momentum":1},
        {"time":"t1","scale":"1m","trend":1,"momentum":1},
        {"time":"t2","scale":"1d","trend":-1,"momentum":-1},
        {"time":"t2","scale":"1w","trend":-1,"momentum":-1},
        {"time":"t2","scale":"1m","trend":-1,"momentum":-1},
    ]}
    states=daily_wave_states(field)
    assert [(s["time"],s["direction"]) for s in states]==[("t1",1),("t2",-1)]
