#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import time
from importlib import reload

import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import Utils
import telebot

reload(sys)
path = os.path.dirname(os.path.abspath(__file__))
u = Utils(path)
bot = telebot.TeleBot(u.get_token())

# File to have a history about the files that was downloaded
path_file_downloaded = os.path.join(path, 'files.txt')
files_downloaded = [line.rstrip('\n').split(" ")[1] for line in open(path_file_downloaded, 'a+')]


def get_name_from_message(m):
    bigger_size = 0
    file_info = 0
    file_name = 0

    if m.content_type == 'photo':
        # we receive tree types of size from telegram api and we select the biggest size
        for photo in m.photo:
            if photo.file_size > bigger_size:
                bigger_size = photo.file_size
                file_info = bot.get_file(photo.file_id)
                file_name = photo.file_id
    elif m.content_type == 'video_note':
        file_info = bot.get_file(m.video_note.file_id)
        file_name = m.video_note.file_id
    elif m.content_type == 'video':
        file_info = bot.get_file(m.video.file_id)
        file_name = m.video.file_id
    elif m.content_type == 'voice':
        file_info = bot.get_file(m.voice.file_id)
        file_name = m.voice.file_id

    return file_name, file_info


def listener(messages):
    """
    Check if the message that receive from telegram is photo, video, video_note (aka video petit) or voice
    and create a bot message to know if the user save or not the file
    """
    for m in messages:
        try:
            file_name, file_info = get_name_from_message(m)
            if file_name not in files_downloaded:
                if m.content_type in ['photo', 'video_note', 'video', 'voice']:
                    # Text to know if the user want to save the file or not
                    markup = InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton("Yeah", callback_data="upload"),
                               InlineKeyboardButton("Nope", callback_data="not_upload"))
                    bot.send_message(chat_id=m.chat.id, reply_to_message_id=m.message_id,
                                     text="<b>Do you want to save the file?</b>", parse_mode='HTML',
                                     disable_notification=True, reply_markup=markup)
            else:
                bot.send_message(text="<b>This file has already been saved</b>", chat_id=m.chat.id,
                                      parse_mode='HTML', reply_to_message_id=m.message_id, reply_markup=None)
        except Exception as e:
            print(e)


def main():

    @bot.callback_query_handler(func=lambda call: True)
    def callbacks(m):
        text_to_show = ''

        # Check if the user want to saver or not
        if m.data == 'upload':
            origin_message = m.message.reply_to_message
            file_name, file_info = get_name_from_message(origin_message)

            # Check if the file was downloaded previously
            if file_name not in files_downloaded:
                # add new file to the record
                files_downloaded.append(file_name)
                aux = open(path_file_downloaded, 'a')
                aux.write('{} {}\n'.format(datetime.date.today().strftime('%Y-%m-%d'), file_name))
                aux.close()

                downloaded_file = bot.download_file(file_info.file_path)
                # Control to know if the group want to save the file
                path_to_save = os.path.join(path, "files", str(m.message.chat.id).replace("-", "neg"))
                if not os.path.exists(path_to_save):
                    os.makedirs(path_to_save)
                with open(os.path.join(path_to_save, '{} {}.{}'.format(datetime.date.today().strftime('%Y-%m-%d'),
                                                                        file_name,
                                                                        'jpg' if origin_message.content_type == 'photo'
                                                                        else 'ogg')),
                          'wb') as new_file:
                    new_file.write(downloaded_file)

            text_to_show = '<b>Yeah! You save the file :D</b>'
        elif m.data == 'not_upload':
            text_to_show = "<b>Hi policeman, I didn't see anything :|</b> <i>(Don't save)</i>"
        bot.edit_message_text(text=text_to_show, chat_id=m.message.chat.id, parse_mode='HTML',
                              message_id=m.message.message_id, reply_markup=None)

    while True:
        try:
            # If the bot has a error, with none_stop = true he never stop ?
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)


if __name__ == '__main__':
    if not os.path.exists(os.path.join(path, "files")):
        os.makedirs(os.path.join(path, "files"))
    bot.set_update_listener(listener)
    main()
