from kebab import literal
from kebab.loader import YamlLoader, IniLoader


def load_content(filename):
    with open(filename) as fp:
        return fp.read()


def test_yaml_loader():
    loader = YamlLoader()
    result = loader.load(load_content("tests/data/conf1.yaml"))
    assert result['string_field'] == "better value"


def test_ini_loader():
    loader = IniLoader()
    conf = loader.load(load_content("tests/data/conf.ini"))

    assert conf['default']['string_field'] == "better value"

    assert conf['profile1']['string_field'] == "best value"

    result = literal(**conf["profile1"])
    assert result.get('int_field', expected_type=int) == 100
