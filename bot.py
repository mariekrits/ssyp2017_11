import config
import telebot
from telebot import types
from PIL import Image, ImageOps
from matplotlib import image
import numpy as np
import requests
from io import BytesIO
import strings
import os
from flask import Flask, request

token = '431689751:AAH_sZLwpdsFV4KzdvPLw2REYqfPeTbPwU4'
bot = telebot.TeleBot(token)
server = Flask(__name__)

# TODO: пофиксить хэндлеры
# TODO: запилить поддержку нескольких пользователей
# TODO: привести код к нормальному виду
# TODO: склеить бота и распознавание
# TODO: прихерачить сверху разрезание на символы
# TODO: протестить
# TODO: кайфовать


# modes: 0 - inactive, 1 - recognize mode, 2 - cut mode
chat_ids = {}


def binarize(pixels):
    hist = [0 for x in range(256)]
    for i in pixels:
        for j in i: hist[j] += 1

    m = 0
    n = 0
    for i in range(256):
        m += hist[i] * i
        n += hist[i]
    a = 0
    b = 0
    max_hist = 0
    max_i = 0
    for j in range(1, 256):
        a += hist[j] * j
        b += hist[j]
        if b == 0:
            continue
        v1 = b / n
        v2 = 1 - v1
        n1 = a / b
        n2 = (m - a) / (n - b)
        vn = v1 * v2 * (n2 - n1) ** 2
        if max_hist < vn:
            max_hist = vn
            max_i = j

    pixels[pixels >= max_i] = 255
    pixels[pixels < max_i] = 0
    return pixels


def cut(pixels, w, h):
    print('in cut 1')
    line = []
    simb = []
    count = 0
    count1 = 0

    img_arr = []  # array of cut symbols

    for i in range(h):
        for j in range(w):
            if pixels[i, j] == 0:
                count += 1
        if w > count > 0 and len(line) % 2 == 0:
            line.append(i)
            # for j in range(w):
            #    pixels[i, j] = 0
        elif count == 0 and len(line) % 2 != 0 or count == w and len(line) % 2 != 0:
            for j in range(w):
                if pixels[i - 1, j] == 0:
                    count1 += 1
            if count1 == 0:
                line.append(i)
            count1 = 0
            # for j in range(w):
            #   pixels[i - 1, j] = 0
        count = 0
    print('in cut 2')
    for a in range(len(line) // 2):
        print('lol kek cheburek')
        h = line[2 * a + 1] - line[2 * a] + 1
        tmp_1 = pixels[line[2 * a] - 1: line[2 * a + 1] + 1, :w]
        print('sleep')
        print(w, h)
        print(tmp_1.shape)
        tmp_1 = np.reshape([tmp_1[i, j] for j in range(h) for i in range(w)], (h, w))
        print('sleep' * 2)
        simb.clear()
        print('sleep' * 3)
        for j in range(w):
            print('sleep' * 4)
            for i in range(h):
                if tmp_1[i, j] == 0:
                    count += 1
            if count > 0 and len(simb) % 2 == 0:
                simb.append(j)
            elif count == 0 and len(simb) % 2 != 0:
                simb.append(j - 1)
            count = 0
        for i in range(0, len(simb), 2):
            print('lol kek cheburek 2')
            tmp_2 = tmp_1[0: h, simb[i] - 1: simb[i + 1] + 2]
            # filename = 'simb' + str(a) + '.' + str(i // 2) + '.png'
            # image.imsave(filename, tmp_2, vmin=0, vmax=255, cmap="gray", origin='upper')
            img_arr.append(tmp_2)
    print('in cut 3')
    return img_arr


def extract_image_from_message(message):
    if not message.photo:
        return
    file_id = None
    min_size = -1
    for photo in message.photo:
        w, h = photo.width, photo.height
        if min_size == -1 or w * h < min_size:
            min_size = w * h
            file_id = photo.file_id
    pic_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, bot.get_file(file_id).file_path)
    img = requests.get(pic_url).content
    img = Image.open(BytesIO(img))
    img = img.resize((w, h), Image.ANTIALIAS).convert('L')
    return w, h, img


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('/cut', '/recognize', '/info')

    bot.send_message(message.chat.id, strings.start, reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    id = message.chat.id
    if id not in chat_ids or chat_ids[id] == 0:
        return
    bot.send_message(message.chat.id, "Подождите...")
    w, h, img = extract_image_from_message(message)
    pixels = binarize(np.array(img))
    if chat_ids[id] == 1:
        bot.send_message(id, 'как раз')
    elif chat_ids[id] == 2:
        img_arr = cut(pixels, w, h)
        for img in img_arr:
            print('lol kek')
            bot.send_photo(id, img.tobytes())
    chat_ids.pop(id)


@bot.message_handler(commands=['cut'])
def handle_cutsimb(message):
    bot.send_message(message.chat.id, "Отправьте фото.")
    chat_ids[message.chat.id] = 2


@bot.message_handler(commands=['recognize'])
def handle_cutsimb(message):
    bot.send_message(message.chat.id, "Отправьте фото.")
    chat_ids[message.chat.id] = 1


@bot.message_handler(commands=['info'])
def handle_start_help(message):
    bot.send_message(message.chat.id, strings.alex_stats)
    bot.send_message(message.chat.id, strings.ghen_stats)
    bot.send_message(message.chat.id, strings.ilyag_stats)
    bot.send_message(message.chat.id, strings.ilyam_stats)
    bot.send_message(message.chat.id, strings.max_stats)
    bot.send_message(message.chat.id, strings.mari_stats)
    bot.send_message(message.chat.id, strings.master_stats)


@server.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


bot.remove_webhook()
bot.set_webhook(url=config.HOST + "/bot")

server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
server = Flask(__name__)
