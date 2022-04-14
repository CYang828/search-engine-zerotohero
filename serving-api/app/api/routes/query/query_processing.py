# @Time    : 2022-01-10 15:03
# @Author  : Li Mengqi
# @File    : query_processing.py

from fastapi import APIRouter
from app.models.schemas.query import QueryProcessingResonse, QueryProcessingArgs
from app.resources.api_response import ApiResponse, ResponseEnum
from query.preprocessing import QueryPre
from query.sensitive_filter import DFAFilter
from query.tokenization import Tokenization
from query.rewrite import RewriteQuery
from query.intent_recognition import IntentRecognition

router = APIRouter()
query_pre = QueryPre()
filter = DFAFilter()
tokenizer = Tokenization()
rewrite = RewriteQuery()
intentrecog = IntentRecognition()


@router.get('/processing', name="query:processing", summary='query processing', response_model=QueryProcessingResonse)
async def understanding(args: QueryProcessingArgs):
    """
    query 理解
    - params: sentence 请求体参数->json
    - return: 暂时愿样子返回
    """
    results = []
    sentence = args.sentence
    if not sentence.strip():
        return ApiResponse.build_error(ResponseEnum.QUERY_UNDERSTANDING_ERROR)
    if args.process_type == 'default':
        # query预处理：过滤emo、大写转小写、半角转全角、繁体转简体
        sentence = query_pre.run(args.sentence)
        # 敏感识别
        sentence = filter.filter(sentence)
        # 纠错后
        sentence = rewrite.query_corrector(sentence)
        # query分词与实体识别
        sentence_tokens, sentence_entity = tokenizer.hanlp_token_ner(sentence)
        # rewrite
        # 归一
        sentence_unify = rewrite.query_unify(sentence_tokens)
        # 扩展
        sentence_extend = rewrite.query_extend(sentence_tokens)
        # 意图识别(返回的是文章集)
        documents = intentrecog.predict(sentence)
        results.extend([sentence, sentence_tokens, sentence_entity, sentence_unify, sentence_extend])
    elif args.process_type == 'tokens':
        sentence_tokens, _ = tokenizer.hanlp_token_ner(sentence)
        results.append(sentence_tokens)
    elif args.process_type == 'ner':
        _, sentence_entity = tokenizer.hanlp_token_ner(sentence)
        results.append(sentence_entity)
    elif args.process_type == 'preprocess':
        sentence = query_pre.run(args.sentence)
        results.append(sentence)
    elif args.process_type == 'filter_sensitive':
        sentence = filter.filter(sentence)
        results.append(sentence)
    elif args.process_type == 'corrector':
        sentence = rewrite.query_corrector(sentence)
        results.append(sentence)
    elif args.process_type == 'unify':
        sentence_tokens, _ = tokenizer.hanlp_token_ner(sentence)
        sentence_unify = rewrite.query_unify(sentence_tokens)
        results.append(sentence_unify)
    elif args.process_type == 'extend':
        sentence_tokens, _ = tokenizer.hanlp_token_ner(sentence)
        sentence_extend = rewrite.query_extend(sentence_tokens)
        results.append(sentence_extend)
    elif args.process_type == 'intent_recognition':
        documents = intentrecog.predict(sentence)
        results.append(documents)
    else:
        ApiResponse.build_error(ResponseEnum.QUERY_UNDERSTANDING_ERROR)
    return ApiResponse.build_success(data={'query_processing': results})
