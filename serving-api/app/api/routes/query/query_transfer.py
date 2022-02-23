# @Time    : 2022-01-10 15:03
# @Author  : Li Mengqi
# @File    : query_transfer.py

from fastapi import APIRouter
from app.models.schemas.query import QueryTransferResonse, SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum
from app.services.query.query_preprocess import QueryPre
from app.services.query.rewrite_query import RewriteQuery
from app.services.query.sensitive_filter import DFAFilter
rewritequery = RewriteQuery()  # query改写类
gfw = DFAFilter()

router = APIRouter()


@router.get('/transfer', name="query:transfer", summary='query transfer', response_model=QueryTransferResonse)
async def transfer(args: SentenceArgs):
    """
    本部分包括query的预处理、归一、敏感识别
    - params: sentence 请求体参数->json
    - return: 暂时愿样子返回
    """
    # 1、判断参数的合法性
    query = args.sentence  # 获取query
    if isinstance(query, str):  # 判断是不是字符数据类型
        query = query
    elif isinstance(query, bytes):  # 如果是字节型转换为字符型
        query = query.decode("utf-8", "ignore")
    else:
        return ApiResponse.build_error(ResponseEnum.QUERY_TYPE_ERROR)  # 字符串不合法返回报错信息
    try:
        # 2、预处理
        querypre = QueryPre()  # 新建预处理对象
        query = querypre.capital_to_lower(query)  # 大写转小写
        query = querypre.strB2Q(query)  # 半角转全角
        query = querypre.t2s_by_opencc(query)  # 繁体转简体
        query = querypre.filter_emoji(query)  # 过滤表情
        # 3、query纠错  # 该部分需要加载模型，需要时间较长，所以把其实例化的过程放在了本py文件的开头，项目启动即实例化
        query = rewritequery.grammer_corrector(query)
        # 4、query归一
        # query = rewritequery.query_unify(query) # 还需要改进
        # 5、query扩展  # 该方法还不成熟还需要更新
        # 4、敏感识别
        query = gfw.filter(query)
    except Exception as e:
        return ApiResponse.build_error(ResponseEnum.QUERY_TRANSFER_ERROR)  # transfer过程出现问题
    return ApiResponse.build_success(data={'query': 'query transfer results {}'.format(query)})
