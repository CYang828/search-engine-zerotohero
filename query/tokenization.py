# -*- coding:utf-8 -*-
# @Time   :2022/3/8 1:58 下午
# @Author :Li Meng qi
# @FileName:tokenization.py
import hanlp


class Tokenization:
    def __init__(self):
        # 先加载模型
        self.HanLP = hanlp.load(
            hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH
        )

    def hanlp_token_ner(self, query):
        """
        调用hanlp分词
        :param query: 一句话
        :return: 分词结果
        """
        # 这里如果是空下面的分词会报错
        if query.strip() == "":
            return [""]
        # 精分&实体识别
        results_document = self.HanLP(query, tasks="ner")
        return results_document["tok/fine"], results_document["ner/msra"]


if __name__ == "__main__":
    tokenize = Tokenization()
    print(
        tokenize.hanlp_token(
            "众所周知，长时间以来，加入欧盟和北约，就是乌克兰政府的心愿。过去这段时间里，为了加入北约和欧盟，乌克兰政府曾多次向其喊话，要求其同意乌克兰的加入。而自俄乌冲突正式开始后，乌克兰总统泽连斯基喊话欧盟与北约的频率更是越发频繁，就在前几日，泽连斯基更是发表了视频讲话，并在视频讲话中呼吁欧盟启动特殊程序，立即同意乌克兰加入欧盟。"
        )
    )
