
import re
import collections
import configparser


def utf8(d):
    if isinstance(d, bytes):
        return d.decode('utf-8')
    if isinstance(d, dict):
        return dict(map(utf8, d.items()))
    if isinstance(d, tuple):
        return map(utf8, d)
    return d


def str2everything(s):
    """convert str to the most possibility type
    support type:
        int
        float
        boolean: yes, no
        str,
        list
    """

    try:
        # int, float
        c = eval(s)
        if isinstance(c, (int, float)):
            return c
        else:
            return utf8(s)
    except NameError:
        # boolean, str, list
        if s.lower() == 'yes':
            return True
        elif s.lower() == 'no':
            return False
        elif len(s.split(',')) > 1:
            return [i for i in s.split(',') if i]
        else:
            return utf8(s)
    except (SyntaxError, TypeError):
        return utf8(s)


class ConfigurationParser(object):
    """Configuration Parser"""

    parser = {'ini': '_ini_parser'}

    def __init__(self, t, **setting):
        """parse config file
        :parameter:
          - `t`: type
          - `setting`: setting
        parse result:
            `configs`: {'section': {setting}}
        """
        self.configs = None
        self.get_configs(t, setting)

    @staticmethod
    def _check_setting(eattr, setting):
        """check backend setting
        :parameter:
          - `eattr`: essential attribute
          - `setting`: setting
        """

        for attr in eattr:
            v = setting.get(attr)

    #         if not v:
    #             recorder('CRITICAL', 'configuration backend setting error! '
    #                                  'right options {options}'.format(options=eattr))
    #             raise ParameterError

    def _ini_parser(self, setting):
        """ini file parser
        :parameter:
          - `setting`: setting
        """
        eattr = ['path']
        self._check_setting(eattr, setting)
        path = setting.get('path')
        # path : 'config.ini'文件
        cf = configparser.ConfigParser()
        cf.read(path)

        configs = collections.defaultdict(dict)

        for section in cf.sections():
            options = cf.items(section)
            for key, value in options:
                value = str2everything(value)
                configs[section][key] = value
        return configs

    def get_configs(self, t, setting):
        """get configs from the type
        :parameter:
          - `backend`: type
          - `setting`: setting
        """
        parser = self.parser.get(t)
        if parser:
            # 执行 _ini_parser函数，传入setting
            self.configs = getattr(self, parser)(setting)

        else:
            raise ParameterError


class ParameterError:
    """参数错误"""
    pass
