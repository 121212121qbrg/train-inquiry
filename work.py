# Import necessary modules
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config

import sys
import json
import requests
import spacy
import numpy as np

import urllib3
import json
import urllib
import time
import urllib.request

# Create a trainer that uses this config
trainer = Trainer(config.load("config_spacy.yml"))

# Load the training data
training_data = load_data('demo-rasa.json')

# Create an interpreter by training the model
interpreter = trainer.train(training_data)



nlp = spacy.load("en_core_web_md")


state = {}              # state存储出发地目的地和时间
message = ''            # 存用户输入
respond = 'init'        # 存机器人说的话的种类
last = ''               # 上一个回复


def my_init():
    global respond
    global state
    global last
    global message
    print("hello,I can help you search for train ticket information.")
    respond = 'init'
    last = "Please enter the place of departure and the time of arrival.(Can only inquire about nearly a month) \nFor example:\nI would like to check the train from Guangzhou to Xian on 2019-09-01."
    print(last)
    while 1==1:
        input_message()    #开始对话
    return None


def input_message():
    # Iterate over the word's ancestors
    global message
    message = input()
    data = interpreter.parse(message)
    if data['intent']['confidence'] >0.3:
        message_name = data['intent']['name']
    else:
        message_name = "default"
    #print(message_name, data['intent']['confidence'])
    respond_message(message_name)


    # print(message_name,data['intent']['confidence'])
    # data['intent']['name']
    return None


def respond_message(message_name):
    global respond
    global state
    global last
    global message
    if message_name == "goodbye":
        state.clear()
        respond = "goodbye"
        last = "goodbye"
        print(last)
        time.sleep(3)
        sys.exit()
        # 对话结束

    elif message_name == "greet":
        print("hello")
        print("ummm......")
        print(last)
        #继续之前的对话

    elif respond == "init":
        if message_name == "train_info":
           # print("111111")
            get_info()    # 获取信息
            check_info()  # 检测信息全不全
        else:
            print("......sorry,I can't understand")
            print(last)
            # 继续之前的对话

    elif respond == "ask_start":
        doc = nlp(message)
        gpe_num = 0
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                gpe_num = gpe_num + 1

        if gpe_num == 0:
            print("......sorry,I can't understand")
            print(last)

        elif gpe_num == 1:
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    state['start_place'] = ent.text
            print("ok, the starting station is {}".format(state['start_place']))
            check_info()  # 检测信息全不全

        else:
            s_word = []
            che = 0
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    s_word.clear()
                    start_list = list(doc[ent.start].ancestors)
                    for s_l in start_list:
                        s_word.append(s_l.text)
                    if 'from' in s_word:
                        state['start_place'] = ent.text
                        che = 1
            if che == 1:
                print("ok, the starting station is {}".format(state['start_place']))
                check_info()  # 检测信息全不全
            else:
                print("......sorry,I can't understand")
                print(last)
    elif respond == "ask_end":
        doc = nlp(message)
        gpe_num = 0
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                gpe_num = gpe_num + 1

        if gpe_num == 0:
            print("......sorry,I can't understand")
            print(last)

        elif gpe_num == 1:
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    state['end_place'] = ent.text
            print("ok, the ending station is {}".format(state['end_place']))
            check_info()  # 检测信息全不全

        else:
            s_word = []
            che = 0
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    s_word.clear()
                    end_list = list(doc[ent.start].ancestors)
                    for s_l in end_list:
                        s_word.append(s_l.text)
                    if 'from' in s_word:
                        state['end_place'] = ent.text
                        che = 1
            if che == 1:
                print("ok, the ending station is {}".format(state['end_place']))
                check_info()  # 检测信息全不全
            else:
                print("......sorry,I can't understand")
                print(last)
    elif respond == "ask_time":
        if message_name == "time_info":
            get_info()    # 获取信息
            check_info()  # 检测信息全不全
        else:
            print("......sorry,I can't understand")
            print(last)
            # 继续之前的对话
    elif respond == "end_round":
        respond = 'init'
        last = "Please enter the place of departure and the time of arrival.(Can only inquire about nearly a month) \nFor example:\nI would like to check the train from Guangzhou to Xian on 2019-09-01."
        print(last)
        #继续之前的对话
    else:
        print("......sorry,I can't understand")
        print(last)
    return None


def get_info():
    global respond
    global state
    global last
    global message

    entities = interpreter.parse(message)["entities"]
    #print(entities)
    params = {}
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])
    # print(params)
    # print("haha")
    for key, value in params.items():
        state[key] = value

    if 'month' in params.keys() and 'day' in params.keys():
        print("setting {}-{} as date".format(state['month'], state['day']))
    if 'start_place' in params.keys():
        print("setting {} as starting station".format(state['start_place']))
    if 'end_place' in params.keys():
        print("setting {} as ending station".format(state['end_place']))
    # 打印信息
    return None


def check_info():
    global respond
    global state
    global last
    global message
    if 'start_place' not in state.keys():
        last = "Where is the starting place?"
        respond = 'ask_start'
        print(last)
    elif 'end_place' not in state.keys():
        last = "Where is the ending place?"
        respond = 'ask_end'
        print(last)
    elif 'month' not in state.keys():
        last = "What is the date of departure? (example:2001-02-03)"
        respond = 'ask_time'
        print(last)
    elif 'day' not in state.keys():
        last = "What is the date of departure?(example:2001-02-03)"
        respond = 'ask_time'
        print(last)
    else:
        print("the starting station is {}\nthe ending station is {}\nthe time is {}-{}\n".format(state["start_place"],state["end_place"],state["month"],state["day"]))
        print("Just a minute, please. Finding results")
        jisuapi_get_reuslt()
    return None

def youdao_translate(word):
    # 有道词典 api
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    # 传输的参数，其中 i 为需要翻译的内容
    key = {
        'type': "AUTO",
        'i': word,
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "ue": "UTF-8",
        "action": "FY_BY_CLICKBUTTON",
        "typoResult": "true"
    }
    # key 这个字典为发送给有道词典服务器的内容
    response = requests.post(url, data=key)
    # 判断服务器是否相应成功
    if response.status_code == 200:
        # 然后相应的结果
        return response.text
    else:
        print("有道词典调用失败")
        # 相应失败就返回空
        return None

def youdao_get_reuslt(repsonse):
    # 通过 json.loads 把返回的结果加载成 json 格式
    result = json.loads(repsonse)
    # print ("输入的词为：%s" % result['translateResult'][0][0]['src'])
    # print ("翻译结果为：%s" % result['translateResult'][0][0]['tgt'])
    return result['translateResult'][0][0]['tgt']

def jisuapi_get_reuslt():
    global respond
    global state
    global last
    global message
    data = {}
    data["appkey"] = "b6fa049c679c2e66"  # 我自己的apikey

    list_trans = youdao_translate(state['start_place'])
    data["start"] = youdao_get_reuslt(list_trans)

    list_trans = youdao_translate(state['end_place'])
    data["end"] = youdao_get_reuslt(list_trans)

    # t_a = '{}-{}-{}'.format(time.strftime("%Y", time.localtime()), 1, 1)
    # t_b = time.strftime("%Y-%m-%d", time.localtime())

    if time.localtime(time.time())[1]> int(state['month']) or( time.localtime(time.time())[1]== int(state['month']) and time.localtime(time.time())[2]> int(state['day'])):
        data["date"] = '{}-{}-{}'.format(time.localtime(time.time())[0]+1, state['month'], state['day'])
    else:
        data["date"] = '{}-{}-{}'.format(time.localtime(time.time())[0], state['month'], state['day'])

    url_values = urllib.parse.urlencode(data)
    url = "https://api.jisuapi.com/train/ticket" + "?" + url_values
    request = urllib.request.Request(url)
    result = urllib.request.urlopen(request)
    jsonarr = json.loads(result.read())

    if jsonarr["status"] != 0:
        print('search error:',jsonarr["msg"])


    else:
        result = jsonarr["result"]
        print('{:15}\t{:15}\t{:15}\t{:15}\t{:15}'.format("trainno", "start station", "end station","departure time", "arrival time"))
        for val in result["list"]:
            if val["canbuy"] == 'Y':
                print('{:15}\t{:15}\t{:15}\t{:15}\t{:15}'.format(val["trainno"], val["station"], val["endstation"], val["departuretime"], val["arrivaltime"]))

    last ='Enter anything for the next round of queries'
    respond = 'end_round'
    state.clear()
    print(last)
my_init()

