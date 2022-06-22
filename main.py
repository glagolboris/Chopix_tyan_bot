import os
import random
import time
import speech_recognition as sr
from os import path
import torch
import telebot
import api as token
import subprocess

class Assistant:
    def stt(self, filename):
        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), filename)
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language='ru-RU')
                return text
            except sr.UnknownValueError:
                return "Извините, я вас не поняла 3:"
            except sr.RequestError as e:
                print(e)
                return "Ошибка сервиса; Обратитесь к @molerzz"

    def tts(self, text):
        torch.backends.quantized.engine = "qnnpack"
        torch.set_num_threads(4)
        model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                  model='silero_tts',
                                  language='ru',
                                  speaker='ru_v3')
        model.to('cpu')

        file = model.save_wav(text=text, speaker='kseniya', sample_rate=48000, put_accent=True, put_yo=True)

        return file

    def to_wav(self, file_name):
        src_filename = file_name
        dest_filename = file_name + '.wav'
        process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
        return dest_filename




class Bot:
    def __init__(self):
        self.assistant = Assistant()
        self.bot = telebot.TeleBot(token=token.tok)
        self.chopix_id = ''
        self.handler()

    def handler(self):
        @self.bot.message_handler(content_types=['voice'])
        def voice_handler(message):
            if str(message.chat.id) == self.chopix_id:
                file_info = self.bot.get_file(message.voice.file_id)
                file = self.bot.download_file(file_info.file_path)
                file_name = str(random.randint(100, 999)) + str(random.randint(100, 999))
                with open(file_name + '.ogg', 'wb') as f:
                    f.write(file)
                infoForwav = self.assistant.to_wav(file_name + '.ogg')
                text = self.assistant.stt(infoForwav)
                os.remove(infoForwav)
                os.remove(file_name + '.ogg')
                if text != 'Извините, я вас не поняла 3:' and text != 'Ошибка сервиса; Обратитесь к @molerzz':
                    self.bot.send_message(self.chopix_id, f'@{message.from_user.username} сказал: ' + text,
                                          reply_to_message_id=message.message_id)
                else:
                    self.bot.send_message(self.chopix_id, text, reply_to_message_id=message.message_id)


        @self.bot.message_handler(commands=['say'])
        def say(message):
            if str(message.chat.id) == self.chopix_id:
                try:
                    text = message.text.split('/say ')[1]
                    file = self.assistant.tts(text)
                    self.bot.send_message(self.chopix_id, 'Записываю гс... ༼ つ ◕_◕ ༽つ',
                                          reply_to_message_id=message.message_id)
                    sticker = open('stickers/sticker2.webp', 'rb')
                    self.bot.send_sticker(self.chopix_id, sticker)
                    time.sleep(3)
                    self.bot.send_voice(self.chopix_id, open(file, 'rb'))
                    os.remove(file)
                except IndexError:
                    self.bot.send_message(self.chopix_id,
                                          'Извини, но здесь нет текста. ¯\_(ツ)_/¯ \nДля того, чтобы я что-то сказала введи "/say <твой-текст>"!',
                                          reply_to_message_id=message.message_id)
                    sticker = open('stickers/sticker.webp', 'rb')
                    self.bot.send_sticker(self.chopix_id, sticker)

                except ValueError:
                    self.bot.send_message(message.chat.id, 'Прости, я разговариваю только на русскому языке(( ????',
                                          reply_to_message_id=message.message_id)
                    sticker = open('stickers/sticker3.webp', 'rb')
                    self.bot.send_sticker(message.chat.id, sticker)

            else:
                print('say')


while True:
    try:
        bot = Bot()
        bot.bot.polling(none_stop=True, interval=0)
    except Exception:
        continue
