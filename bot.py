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


# recognize_mode = False
# cut_mode = False


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('/cut', '/recognize', '/info')

    bot.send_message(message.chat.id, strings.start, reply_markup=markup)


@bot.message_handler(commands=['cut'])
def handle_cutsimb(message):
    # global cut_mode
    bot.send_message(message.chat.id, "Отправьте фото.")

    # cut_mode = True

    @bot.message_handler(content_types=['photo'])
    def handle_photo_cut(message):
        bot.send_message(message.chat.id, "Подождите...")
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
        pixels = np.array(img)

        hist = [0 for x in range(256)]
        for i in pixels:
            for j in i: hist[j] += 1
        print(hist)

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
        print('max_i =', max_i)

        def convert_to_01(px):
            if px == 255:
                return 0
            return 1

        pixels[pixels >= max_i] = 255
        pixels[pixels < max_i] = 0

        line = []
        simb = []
        count = 0
        count1 = 0

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
        for i in range(0, len(line), 2):
            tmp_1 = pixels[line[i] - 1: line[i + 1] + 1, 0: w]
            image.imsave('line' + str(i // 2) + '.png', tmp_1, vmin=0, vmax=255, cmap="gray", origin='upper')
        print('line=', len(simb))
        for a in range(len(line) // 2):
            print(a)
            img = Image.open('line' + str(a) + '.png').convert('L')
            w, h = img.size
            tmp_1 = img.load()
            tmp_1 = np.reshape([tmp_1[i, j] for j in range(h) for i in range(w)], (h, w))
            simb.clear()
            for j in range(w):
                for i in range(h):
                    if tmp_1[i, j] == 0:
                        count += 1
                if count > 0 and len(simb) % 2 == 0:
                    simb.append(j)
                elif count == 0 and len(simb) % 2 != 0:
                    simb.append(j - 1)
                count = 0
            print(simb)
            for i in range(0, len(simb), 2):
                tmp_2 = tmp_1[0: h, simb[i] - 1: simb[i + 1] + 2]
                image.imsave('simb' + str(a) + '.' + str(i // 2) + '.png', tmp_2, vmin=0, vmax=255, cmap="gray",
                             origin='upper')
                bot.send_photo(message.chat.id, open('simb' + str(a) + '.' + str(i // 2) + '.png', 'rb'))


@bot.message_handler(commands=['recognize'])
def handle_cutsimb(message):
    # global recognize_mode
    bot.send_message(message.chat.id, "Отправьте фото.")

    # recognize_mode = True

    @bot.message_handler(content_types=['photo'])
    def handle_photo_cut(message):
        bot.send_message(message.chat.id, "Подождите...")
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
        pixels = np.array(img)

        hist = [0 for x in range(256)]
        for i in pixels:
            for j in i: hist[j] += 1
        print(hist)

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

        def convert_to_01(px):
            if px == 255:
                return 0
            return 1

        pixels[pixels >= max_i] = 255
        pixels[pixels < max_i] = 0

        bot.send_message(message.chat.id, 'На картинке символ " ".')


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
    print("/bot")
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=config.HOST +"/bot")
    return "!", 200

server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
server = Flask(__name__)
webhook()