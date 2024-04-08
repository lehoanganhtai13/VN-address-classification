import time

def test_public_case(solution, test_cases):
    i = 0
    pass_count = 0
    for case in test_cases:
        i += 1

        start = time.time()
        result = solution.process(case['text'])
        stop = time.time()

        pass_value = False
        if result['province'] == case['result']['province'] and result['district'] == case['result']['district'] and result['ward'] == case['result']['ward']:
            pass_value = True
        # print('Pass value:', pass_value)
        pass_time = True if ((stop - start) < 0.1) else False
        # print('Pass time:', pass_value)
        if pass_value == True and pass_time == True:
            pass_count += 1
        else:   
            print(f"Test case {i}: {case['text']}")
            print('result:',result)
            print('answer',case['result'])
            print('')

    assert pass_count == 450
