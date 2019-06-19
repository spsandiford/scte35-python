import pytest

from scte35 import HlsCueTag, NotAnHLSCueTag, MissingCueException

example_good_tags = [
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=,ELAPSED=0.000',
        'components': {
            'TYPE': 52,
            'CUE': '/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=',
            'ELAPSED': 0.0,
        }
    },
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAACfwEAM///wBQb/7oNnJgBJAhxDVUVJOeVySX//AAD/ESIICAAFH4I55XJJNAEDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAADJv9UM=,ELAPSED=176.176',
        'components': {
            'TYPE': 52,
            'CUE': '/DBfAACfwEAM///wBQb/7oNnJgBJAhxDVUVJOeVySX//AAD/ESIICAAFH4I55XJJNAEDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAADJv9UM=',
            'ELAPSED': 176.176,
        }
    },
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x34,DURATION=60.060,CUE-OUT=YES,UPID="0x08:0x9425BC",CUE="/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=",ID="f6UrRd"',
        'components': {
            'TYPE': 52,
            'DURATION': 60.06,
            'CUE-OUT': 'YES',
            'UPID': '0x08:0x9425BC',
            'CUE': '/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=',
            'ID': 'f6UrRd',
        }
    },
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x50,TIME=1448928000.000,ELAPSED=32400.0,CUE="/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=",ID="e+CuqI"',
        'components': {
            'TYPE': 80,
            'TIME': 1448928000.0,
            'ELAPSED': 32400.0,
            'CUE': '/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=',
            'ID': 'e+CuqI',
        }
    },
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=,ELAPSED=100.100',
        'components': {
            'TYPE': 52,
            'CUE': '/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=',
            'ELAPSED': 100.1,
        }
    },
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x35,CUE-IN=YES,CUE="/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=",ID="f6UrRd"',
        'components': {
            'TYPE': 53,
            'CUE-IN': 'YES',
            'CUE': '/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=',
            'ID': 'f6UrRd',
        }
    },
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x10,ELAPSED=0.0,UPID="0x08:0x9425",BLACKOUT=MAYBE,CUE="/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=",ID="dAQ"',
        'components': {
            'TYPE': 16,
            'ELAPSED': 0.0,
            'UPID': '0x08:0x9425',
            'BLACKOUT': 'MAYBE',
            'CUE': '/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=',
            'ID': 'dAQ',
        }
    },
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=,ELAPSED=114.114,SEGNE="3:3"',
        'components': {
            'TYPE': 52,
            'CUE': '/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=',
            'ELAPSED': 114.114,
            'SEGNE': '3:3',
        }
    }
]

example_bad_tags = [
    # Missing "#"
    {
        'tag': 'EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=,ELAPSED=114.114,SEGNE="3:3"',
        'exception': NotAnHLSCueTag,
    },
    # Missing #EXT-X-SCTE35:
    {
        'tag': 'TYPE=0x34,CUE=/DBfAACfwEAM///wBQb/8ZPsgQBJAhxDVUVJOeVyXX//AAD4J5cICAAFH4I55XJdNAIDAilDVUVJAAAAAH+/DBpWTU5VAUB2w2S4qhHoiztw3y+Gas4B+olIUQEAAJOLlf8=,ELAPSED=114.114,SEGNE="3:3"',
        'exception': NotAnHLSCueTag,
    },
    # Missing CUE (Required)
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x10,ELAPSED=0.0,UPID="0x08:0x9425",BLACKOUT=MAYBE,ID="dAQ"',
        'exception': MissingCueException,
    },
    # Empty CUE
    {
        'tag': '#EXT-X-SCTE35:TYPE=0x34,CUE=',
        'exception': MissingCueException,
    }
]


@pytest.fixture(params=example_good_tags)
def good_example_tag(request):
    return request.param


@pytest.fixture(params=example_bad_tags)
def bad_example_tag(request):
    return request.param


def test_good_example_components(good_example_tag):
    result_components = HlsCueTag.tag_components(good_example_tag['tag'])
    for component_name in good_example_tag['components']:
        assert result_components[component_name] == good_example_tag['components'][component_name]


def test_bad_example_components(bad_example_tag):
    with pytest.raises(bad_example_tag['exception']) as e_info:
        HlsCueTag.tag_components(bad_example_tag['tag'])
