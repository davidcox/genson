
import genson


def test_recursion_problem():

    # this one is a problem with the default recursion depth
    genson_string = '''{
                            "a": choice(
                                [
                                    [
                                        {},
                                        {
                                            "a": 0,
                                            "b": {
                                                    "a":
                                                        {"b": [
                                                                {
                                                                    "c": choice([0,1])
                                                                }
                                                              ]
                                                        }
                                                 }
                                        }
                                    ]
                                ])
                        }
                   '''

    # this one is okay
    genson_string2 = '''{
                            "a":
                                [
                                    [
                                        {},
                                        {
                                            "a": 0,
                                            "b": {
                                                    "a":
                                                        {"b": [
                                                                {
                                                                    "c": choice([0,1])
                                                                }
                                                              ]
                                                        }
                                                 }
                                        }
                                    ]
                                ]
                        }
                   '''

    # this one is okay
    genson_string3 = '''{
                            "a": choice([
                                            [
                                                {
                                                    "a": 0
                                                }
                                            ]
                                        ]
                                       )
                        }
                   '''


    # this one is okay
    genson_string4 = '''{
                            "a": choice([
                                            [
                                                {
                                                    "a": choice([{"a": 0}, 3])
                                                }
                                            ]
                                        ]
                                       )
                        }
                   '''

    # this one is okay
    genson_string5 = '''{
                            "a": choice(
                                [
                                    [
                                        {},
                                        {
                                            "a": 0,
                                            "b": {
                                                    "a": [
                                                            {
                                                                    "c": choice([0,1])
                                                            }
                                                          ]
                                                 }
                                        }
                                    ]
                                ])
                        }
                   '''

    # this one is okay
    genson_string6 = '''{
                            "a": choice(
                                [
                                    [
                                        {},
                                        {
                                            "a": 0,
                                            "b": {
                                                    "a":
                                                        {"b": [
                                                                {
                                                                    "c": 1
                                                                }
                                                              ]
                                                        }
                                                 }
                                        }
                                    ]
                                ])
                        }
                   '''

    # this one is a problem
    genson_string7 = '''{
                            "a": choice(
                                [
                                    [
                                        {},
                                        {
                                            "a":
                                                        {"b": [
                                                                {
                                                                    "c": choice([0,1])
                                                                }
                                                              ]
                                                        }

                                        }
                                    ]
                                ])
                        }
                   '''

    genson.loads(genson_string7)
    genson.loads(genson_string6)
    genson.loads(genson_string5)
    genson.loads(genson_string4)
    genson.loads(genson_string3)
    genson.loads(genson_string2)
    genson.loads(genson_string)
