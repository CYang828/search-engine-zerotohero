

from tornado.options import options

from util.configuration import ConfigurationParser


# class Loader(object):
#     """系统全局加载器
#     """

#     def __init__(self):
#         # 配置系统
#         self.configs = None
#         self.configer = None
#         self.component_configers = []

#         # 日志系统
#         self.system_recorder = None
#         self.application_recorder = None

#         # 系统错误码
#         self.errcode = None

#         # 日志是否被设置过
#         self.bRecorder = False

#         # # 增加最大数据量
#         # AsyncHTTPClient.configure(None, max_body_size=1000000000)

#     def load_configuration(self, backend='ini', **setting):
#         """加载配置文件

#         :parameter:
#           - `backend`: 配置方式,目前支持ini
#           - `setting`: 该格式需要的设置参数
#         """
#         self.configer = ConfigurationParser(backend, **setting)
#         self.configs = self.configer.configs

# recorder('INFO', 'load configuration\nbackend:\t{backend}\n'
#                  'setting:\t{setting}\nconfiguration:\t{config}'.format(backend=backend,
#                                                                         setting=setting,
#                                                                         config=self.configs))

# 需要重新定义options
# 在fastapi 中options  是一个大类，但options.config 最终是'config.ini'类似的文件

# app= Loader()
# app.load_configuration(backend='ini', path='config.ini')

# print('>>>>',app.configs)


def load_configs(path='config.ini', func: str = 'recall'):
    options.define('config', default=path,
                   help='this is default config path', type=str)
    configer = ConfigurationParser('ini', path=options.config)
    return configer.configs[func]


if __name__ == "__main__":
    configs = load_configs(func = 'recall')
    print(configs)
