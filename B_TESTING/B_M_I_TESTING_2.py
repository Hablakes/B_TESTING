import csv
import json
import os
import pathlib
import re
import textwrap
import time

import guessit
import numpy
import pyfiglet
import pymediainfo

import matplotlib.pylab as plt

from ascii_graph import Pyasciigraph
from ascii_graph.colors import *
from ascii_graph.colordata import vcolor
from datetime import datetime
from difflib import SequenceMatcher
from imdb import IMDb
from tkinter import filedialog, Tk

date_string = str(datetime.today().strftime('%Y_%m_%d'))

extensions = ('.3gp', '.asf', '.asx', '.avc', '.avi', '.bdmv', '.bin', '.bivx', '.dat', '.disc', '.divx', '.dv',
              '.dvr-ms', '.evo', '.fli', '.flv', '.h264', '.img', '.iso', '.m2ts', '.m2v', '.m4v', '.mkv', '.mov',
              '.mp4', '.mpeg', '.mpg', '.mt2s', '.mts', '.nfo', '.nrg', '.nsv', '.nuv', '.ogm', '.pva', '.qt', '.rm',
              '.rmvb', '.strm', '.svq3', '.ts', '.ty', '.viv', '.vob', '.vp3', '.wmv', '.xvid', '.webm')

index_folder = '~/{0}_MEDIA_INDEX'

username = None


def main():
    separator_3()
    launch_media_index()

    while True:
        media_index_home()


def change_directory_selection():
    print(pyfiglet.figlet_format('CHANGE_DIRECTORY', font='cybermedium'))
    separator_3()
    directory_selection()


def compare_results(results_one, results_two):
    output_one = []

    for line in results_one:
        if line not in results_two:
            output_one.append('REMOVAL: ' + line)

    for line in results_two:
        if line not in results_one:
            output_one.append('ADDITION: ' + line)

    return output_one


def create_media_information_indices():
    create_movie_information_index()
    create_tv_information_index()


def create_movie_information_index():
    movie_results_list = {}

    movie_scan_start = time.time()
    ia = IMDb()

    with open(os.path.expanduser((index_folder + '/MOVIE_VIDEO_FILES_PATHS.csv').format(username)),
              encoding='UTF-8') as m_f_p:
        movie_index = csv.reader(m_f_p)

        for movie_file in sorted(movie_index):
            try:

                movie_filename_key = movie_file[0].rsplit('/', 1)[-1]
                movie_title_key = movie_file[0].rsplit('/')[-2]

                if not movie_filename_key.lower().endswith('.nfo'):

                    if movie_file[0] not in movie_results_list:
                        movie_results_list[movie_file[0]] = {}

                    movie_results_list[movie_file[0]]['MEDIA-PATH'] = movie_file[0]
                    movie_results_list[movie_file[0]]['MEDIA-TYPE'] = str('MOVIE')
                    movie_results_list[movie_file[0]]['FOLDER-NAME'] = movie_title_key
                    movie_results_list[movie_file[0]]['FILE-NAME'] = movie_filename_key

                    try:

                        movie_file_size = os.path.getsize(movie_file[0])
                        movie_file_size_in_mb = (int(movie_file_size) / 1048576)
                        movie_file_size_in_mb_rounded = str(round(movie_file_size_in_mb, 2))
                        movie_results_list[movie_file[0]]['FILE-SIZE'] = movie_file_size_in_mb_rounded

                    except OSError as e:
                        print('OS ERROR / FILE-SIZE: ', e)
                        print('-' * 100, '\n')
                        continue

                    movie_hash = str(str(movie_filename_key) + '_' + str(movie_file_size))
                    movie_results_list[movie_file[0]]['MOVIE-HASH'] = movie_hash

                    try:

                        movie_title = guessit.guessit(movie_filename_key, options={'type': 'movie'})
                        movie_title_to_query = movie_title.get('title')
                        movie_results_list[movie_file[0]]['FILE-TYPE'] = movie_title.get('container')

                    except OSError as e:
                        print('OS ERROR / GUESSIT: ', e)
                        print('-' * 100, '\n')
                        continue

                    try:

                        movie_media_info = pymediainfo.MediaInfo.parse(movie_file[0])

                    except OSError as e:
                        print('OS ERROR / PY_MEDIA_INFO: ', e)
                        print('-' * 100, '\n')
                        continue

                    try:

                        for track in movie_media_info.tracks:
                            if track.track_type == 'General':
                                duration_integer = track.duration
                                movie_results_list[movie_file[0]]['RUN-TIME'] = duration_integer

                            elif track.track_type == 'Video':
                                movie_results_list[movie_file[0]]['RESOLUTION'] = \
                                    str(track.width) + 'x' + str(track.height)

                    except (KeyError, OSError, TypeError, ValueError) as e:
                        print('OS ERROR / PY_MEDIA_INFO (TRACKS): ', e)
                        print('-' * 100, '\n')
                        continue

                    try:

                        movie_imdb = ia.search_movie(movie_title_to_query)

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('IMDB SEARCH ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                        print('-' * 100, '\n')
                        continue

                    try:

                        for movie_search_results in movie_imdb:
                            if movie_search_results['kind'] == 'movie':
                                movie_id = movie_imdb[0].movieID

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('IMDB ID# ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                        print('-' * 100)
                        continue

                    try:

                        movie_info_set = ia.get_movie(movie_id)

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('IMDB INFOSET ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                        print('-' * 100, '\n')
                        continue

                    try:

                        movie_confidence_percentage = round(match_similar_strings(movie_title_to_query.lower(),
                                                                                  movie_search_results['title']), 2)
                        movie_results_list[movie_file[0]]['SEARCH CONFIDENCE PERCENTAGE'] = movie_confidence_percentage

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('CONFIDENCE PERCENTAGE ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                        print('-' * 100, '\n')
                        continue

                    try:

                        if float(movie_confidence_percentage) >= 0.35:

                            try:

                                movie_results_list[movie_file[0]]['GUESSIT SEARCH TERM'] = movie_title_to_query
                                movie_results_list[movie_file[0]]['MOVIE ID #'] = movie_id
                                movie_results_list[movie_file[0]]['TITLE'] = movie_imdb[0]['title']
                                movie_results_list[movie_file[0]]['YEAR'] = movie_info_set['year']
                                movie_results_list[movie_file[0]]['PLOT'] = movie_info_set['plot'][0].split('::')[0]
                                movie_results_list[movie_file[0]]['RATING'] = movie_info_set['rating']

                            except (IOError, KeyError, TypeError, ValueError) as e:
                                print('IMDB GENERAL INFO ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                                print('-' * 100, '\n')
                                continue

                            try:

                                movie_results_list[movie_file[0]]['GENRES'] = []
                                for genre in movie_info_set['genres']:
                                    movie_results_list[movie_file[0]]['GENRES'].append(genre)

                            except (IOError, KeyError, TypeError, ValueError) as e:
                                print('IMDB GENRE ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                                print('-' * 100, '\n')
                                continue

                            try:

                                movie_results_list[movie_file[0]]['DIRECTOR(S)'] = []
                                for director in movie_info_set['directors']:
                                    movie_results_list[movie_file[0]]['DIRECTOR(S)'].append(director['name'])

                            except (IOError, KeyError, TypeError, ValueError) as e:
                                print('IMDB DIRECTOR ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                                print('-' * 100, '\n')
                                continue

                        else:

                            movie_results_list[movie_file[0]]['GUESSIT SEARCH TERM'] = movie_title_to_query
                            movie_results_list[movie_file[0]]['MOVIE ID #'] = []
                            movie_results_list[movie_file[0]]['TITLE'] = []
                            movie_results_list[movie_file[0]]['YEAR'] = []
                            movie_results_list[movie_file[0]]['PLOT'] = []
                            movie_results_list[movie_file[0]]['RATING'] = []
                            movie_results_list[movie_file[0]]['RUN-TIME'] = duration_integer
                            movie_results_list[movie_file[0]]['GENRES'] = []
                            movie_results_list[movie_file[0]]['DIRECTOR(S)'] = []

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('IMDB GENERAL INFO ERROR: ', e, '\n', 'TV SHOW FILE(S): ', movie_file[0])
                        print('-' * 100, '\n')
                        continue

            except (IOError, KeyError, TypeError, ValueError) as e:
                print('INPUT ERROR: ', e, '\n', 'MOVIE FILE(S): ', movie_file[0])
                print('-' * 100, '\n')
                continue

    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)), 'w',
              encoding='UTF-8', newline='') as m_i_i:

        csv_writer = csv.DictWriter(m_i_i, ['MEDIA-PATH', 'MEDIA-TYPE', 'FOLDER-NAME', 'FILE-NAME', 'FILE-SIZE',
                                            'FILE-TYPE', 'RESOLUTION', 'GUESSIT SEARCH TERM', 'MOVIE ID #', 'TITLE',
                                            'YEAR', 'PLOT', 'RATING', 'RUN-TIME', 'GENRES', 'DIRECTOR(S)',
                                            'SEARCH CONFIDENCE PERCENTAGE', 'MOVIE-HASH'])

        for movie_row in movie_results_list.values():
            csv_writer.writerow(movie_row)

    movie_scan_end = time.time()
    readable_movie_scan_time = round(movie_scan_end - movie_scan_start, 2)
    print('MOVIE INFORMATION SCAN COMPLETE - TIME ELAPSED: ', readable_movie_scan_time, 'Seconds')
    separator_3()


def create_tv_information_index():
    tv_results_list = {}
    tv_overview_plots_dict = {}

    tv_scan_start = time.time()
    ia = IMDb()

    with open(os.path.expanduser((index_folder + '/TV_VIDEO_FILES_PATHS.csv').format(username)),
              encoding='UTF-8') as m_f_p:
        tv_index = csv.reader(m_f_p)

        for tv_file in sorted(tv_index):
            try:

                tv_filename_key = tv_file[0].rsplit('/', 1)[-1]
                tv_title_key = tv_file[0].rsplit('/')[-2]

                if not tv_filename_key.lower().endswith('.nfo'):

                    if tv_file[0] not in tv_results_list:
                        tv_results_list[tv_file[0]] = {}

                    tv_results_list[tv_file[0]]['MEDIA-PATH'] = tv_file[0]
                    tv_results_list[tv_file[0]]['MEDIA-TYPE'] = str('TV SHOW')
                    tv_results_list[tv_file[0]]['FOLDER-NAME'] = tv_title_key
                    tv_results_list[tv_file[0]]['FILE-NAME'] = tv_filename_key

                    try:

                        tv_file_size = os.path.getsize(tv_file[0])
                        tv_file_size_in_mb = (int(tv_file_size) / 1048576)
                        tv_file_size_in_mb_rounded = str(round(tv_file_size_in_mb, 2))
                        tv_results_list[tv_file[0]]['FILE-SIZE'] = tv_file_size_in_mb_rounded

                    except OSError as e:
                        print('OS ERROR / FILE-SIZE: ', e)
                        print('-' * 100, '\n')
                        continue

                    tv_hash = str(str(tv_filename_key) + '_' + str(tv_file_size))
                    tv_results_list[tv_file[0]]['TV-HASH'] = tv_hash

                    try:

                        tv_title = guessit.guessit(tv_filename_key, options={'type': 'episode'})
                        tv_title_to_query = tv_title.get('title')
                        g_season_number = tv_title.get('season')
                        g_episode_number = tv_title.get('episode')
                        tv_results_list[tv_file[0]]['FILE-TYPE'] = tv_title.get('container')

                    except OSError as e:
                        print('OS ERROR / GUESSIT: ', e)
                        print('-' * 100, '\n')
                        continue

                    try:

                        tv_media_info = pymediainfo.MediaInfo.parse(tv_file[0])

                    except OSError as e:
                        print('OS ERROR / PY_MEDIA_INFO: ', e)
                        print('-' * 100, '\n')
                        continue

                    try:

                        for track in tv_media_info.tracks:
                            if track.track_type == 'General':
                                duration_integer = track.duration
                                tv_results_list[tv_file[0]]['RUN-TIME'] = duration_integer

                            elif track.track_type == 'Video':
                                tv_results_list[tv_file[0]]['RESOLUTION'] = str(track.width) + 'x' + str(track.height)

                    except (KeyError, OSError, TypeError, ValueError) as e:
                        print('OS ERROR / PY_MEDIA_INFO (TRACKS): ', e)
                        print('-' * 100, '\n')
                        continue

                    try:

                        tv_imdb = ia.search_movie(tv_title_to_query)

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('IMDB SEARCH ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                        print('-' * 100, '\n')
                        continue

                    try:

                        tv_id = tv_imdb[0].movieID

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('IMDB ID# ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                        print('-' * 100, '\n')
                        continue

                    try:

                        tv_info_set = ia.get_movie(tv_id)

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('IMDB INFOSET ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                        print('-' * 100, '\n')
                        continue

                    try:

                        search_confidence_percentage = match_similar_strings(tv_title_to_query.lower(),
                                                                             tv_imdb[0]['title'].lower())
                        tv_results_list[tv_file[0]]['SEARCH CONFIDENCE PERCENTAGE'] = search_confidence_percentage

                    except (IOError, KeyError, TypeError, ValueError) as e:
                        print('CONFIDENCE PERCENTAGE ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                        print('-' * 100, '\n')
                        continue

                    if float(search_confidence_percentage) >= 0.65:

                        try:

                            ia.update(tv_info_set, 'episodes')

                        except (IOError, KeyError, TypeError, ValueError) as e:
                            print('IMDB TV SHOW SEARCH ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                            print('-' * 100, '\n')
                            continue

                        try:

                            tv_show_title = tv_info_set['title']
                            tv_show_year = tv_info_set['year']
                            tv_show_plot = tv_info_set['plot']
                            episode_title = tv_info_set['episodes'][g_season_number][g_episode_number]['title']
                            episode_year = tv_info_set['episodes'][g_season_number][g_episode_number]['year']
                            episode_plot = tv_info_set['episodes'][g_season_number][g_episode_number]['plot']
                            episode_rating = tv_info_set['episodes'][g_season_number][g_episode_number]['rating']

                        except (IOError, KeyError, TypeError, ValueError) as e:
                            print('IMDB TV EPISODE SEARCH ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                            print('-' * 100, '\n')
                            continue

                        try:

                            if tv_show_title not in tv_overview_plots_dict:
                                tv_overview_plots_dict[tv_show_title] = {}
                                tv_overview_plots_dict[tv_show_title]['SHOW'] = str(str(tv_show_title) + ' (' +
                                                                                    str(tv_show_year) + ')')
                                tv_overview_plots_dict[tv_show_title]['PLOT'] = tv_show_plot[0].split('::')[0]

                        except (IOError, KeyError, TypeError, ValueError) as e:
                            print('TV SHOW OVERVIEW PLOT(S) ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                            print('-' * 100, '\n')
                            continue

                        try:

                            tv_results_list[tv_file[0]]['GUESSIT SEARCH TERM'] = tv_title_to_query
                            tv_results_list[tv_file[0]]['TV SHOW ID #'] = tv_id
                            tv_results_list[tv_file[0]]['TV SHOW TITLE'] = tv_show_title
                            tv_results_list[tv_file[0]]['SEASON #'] = g_season_number
                            tv_results_list[tv_file[0]]['EPISODE #'] = g_episode_number
                            tv_results_list[tv_file[0]]['EPISODE TITLE'] = episode_title
                            tv_results_list[tv_file[0]]['YEAR'] = episode_year
                            tv_results_list[tv_file[0]]['PLOT'] = episode_plot.split('::')[0]
                            tv_results_list[tv_file[0]]['RATING'] = round(episode_rating, 2)
                            tv_results_list[tv_file[0]]['RUN-TIME'] = duration_integer

                        except (IOError, KeyError, TypeError, ValueError) as e:
                            print('IMDB GENERAL INFO ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                            print('-' * 100, '\n')
                            continue

                        try:

                            tv_results_list[tv_file[0]]['GENRES'] = []
                            for genre in tv_info_set['genres']:
                                tv_results_list[tv_file[0]]['GENRES'].append(genre)

                        except (IOError, KeyError, TypeError, ValueError) as e:
                            print('IMDB GENRE ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                            print('-' * 100, '\n')
                            continue

                    else:

                        print('TV SHOW - NO MATCH -', tv_file[0])
                        separator_3()

                        tv_results_list[tv_file[0]]['GUESSIT SEARCH TERM'] = tv_title_to_query
                        tv_results_list[tv_file[0]]['TV SHOW ID #'] = []
                        tv_results_list[tv_file[0]]['TV SHOW TITLE'] = []
                        tv_results_list[tv_file[0]]['SEASON #'] = g_season_number
                        tv_results_list[tv_file[0]]['EPISODE #'] = g_episode_number
                        tv_results_list[tv_file[0]]['EPISODE TITLE'] = []
                        tv_results_list[tv_file[0]]['YEAR'] = []
                        tv_results_list[tv_file[0]]['PLOT'] = []
                        tv_results_list[tv_file[0]]['RATING'] = []
                        tv_results_list[tv_file[0]]['RUN-TIME'] = duration_integer
                        tv_results_list[tv_file[0]]['GENRES'] = []

                        try:

                            tv_show_title = tv_title_to_query

                            if tv_show_title not in tv_overview_plots_dict:
                                tv_overview_plots_dict[tv_show_title] = {}
                                tv_overview_plots_dict[tv_show_title]['SHOW'] = tv_title_to_query
                                tv_overview_plots_dict[tv_show_title]['PLOT'] = str('NO PLOT AVAILABLE')

                        except (IOError, KeyError, TypeError, ValueError) as e:
                            print('TV SHOW OVERVIEW PLOT(S) ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                            print('-' * 100, '\n')
                            continue

            except (IOError, KeyError, TypeError, ValueError) as e:
                print('INPUT ERROR: ', e, '\n', 'TV SHOW FILE(S): ', tv_file[0])
                print('-' * 100, '\n')
                continue

    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)), 'w',
              encoding='UTF-8', newline='') as m_i_i:

        csv_writer = csv.DictWriter(m_i_i, ['MEDIA-PATH', 'MEDIA-TYPE', 'FOLDER-NAME', 'FILE-NAME', 'FILE-SIZE',
                                            'FILE-TYPE', 'RESOLUTION', 'GUESSIT SEARCH TERM', 'TV SHOW ID #',
                                            'TV SHOW TITLE', 'SEASON #', 'EPISODE #', 'EPISODE TITLE', 'YEAR', 'PLOT',
                                            'RATING', 'RUN-TIME', 'GENRES', 'SEARCH CONFIDENCE PERCENTAGE', 'TV-HASH'])

        for tv_row in tv_results_list.values():
            csv_writer.writerow(tv_row)

    with open(os.path.expanduser((index_folder + '/TV_PLOTS_INDEX.csv').format(username)), 'w',
              encoding='UTF-8', newline='') as t_p_i:
        csv_writer = csv.DictWriter(t_p_i, ['SHOW', 'PLOT'])
        for tv_row in tv_overview_plots_dict.values():
            csv_writer.writerow(tv_row)

    tv_scan_end = time.time()
    readable_tv_scan_time = round(tv_scan_end - tv_scan_start, 2)
    print('TV INFORMATION SCAN COMPLETE - TIME ELAPSED: ', readable_tv_scan_time, 'Seconds')
    separator_3()


def directory_selection():
    try:

        global movie_dir_input, tv_dir_input, movie_alt_dir_input, tv_alt_dir_input
        user_info_file = os.path.expanduser((index_folder + '/{0}_USER_INFO.json').format(username))

        print('ENTER PATH OF MOVIE DIRECTORY, IF NONE HIT CANCEL: ')
        movie_dir_input = tk_gui_file_browser_window()
        print('\n', str(movie_dir_input))
        separator_3()

        print('ENTER PATH OF TV DIRECTORY, IF NONE HIT CANCEL: ')
        tv_dir_input = tk_gui_file_browser_window()
        print('\n', str(tv_dir_input))
        separator_3()

        print('ALTERNATE DIRECTORIES? - Y/N: ')
        separator_3()
        alternate_directory_prompt = input('ENTER: Y or N: ').lower()
        separator_3()

        if alternate_directory_prompt == 'y':

            movie_alt_directories_list = list()
            print('ENTER ALTERNATE MOVIE DIRECTORIES, WHEN COMPLETE, HIT CANCEL: ')
            separator_3()
            movie_alt_dir_input = tk_gui_file_browser_window()

            while movie_alt_dir_input != '':
                movie_alt_directories_list.append(movie_alt_dir_input)
                movie_alt_dir_input = tk_gui_file_browser_window()

            print('DIRECTORIES ENTERED: ', '\n', '\n', movie_alt_directories_list)
            tv_alt_directories_list = list()
            separator_3()
            print('ENTER ALTERNATE TV DIRECTORIES, WHEN COMPLETE, HIT CANCEL: ')
            separator_3()
            tv_alt_dir_input = tk_gui_file_browser_window()

            while tv_alt_dir_input != '':
                tv_alt_directories_list.append(tv_alt_dir_input)
                tv_alt_dir_input = tk_gui_file_browser_window()

            print('DIRECTORIES ENTERED: ', '\n', '\n', tv_alt_directories_list)
            separator_3()
            movie_alt_dir_input = movie_alt_directories_list
            tv_alt_dir_input = tv_alt_directories_list
            user_info_dict = {'user:': username, 'movie_dir:': movie_dir_input,
                              'tv_dir:': tv_dir_input, 'movie_alt_dir:': movie_alt_dir_input,
                              'tv_alt_dir:': tv_alt_dir_input}

            with open(user_info_file, 'w', encoding='UTF-8') as json_file:
                json.dump(user_info_dict, json_file, ensure_ascii=False, indent=4, sort_keys=True)

        elif alternate_directory_prompt != 'y':

            print('NO ALTERNATE DIRECTORIES')
            separator_3()
            movie_alt_dir_input = ''
            tv_alt_dir_input = ''
            user_info_dict = {'user:': username, 'movie_dir:': movie_dir_input,
                              'tv_dir:': tv_dir_input, 'movie_alt_dir:': movie_alt_dir_input,
                              'tv_alt_dir:': tv_alt_dir_input}

            with open(user_info_file, 'w', encoding='UTF-8') as json_file:
                json.dump(user_info_dict, json_file, ensure_ascii=False, indent=4, sort_keys=True)

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n')
        separator_3()


def graph_options_advanced(picture_graph_options_int, terminal_graph_options_int):
    m_4k_found_list = []
    m_1080_found_list = []
    m_720_found_list = []
    m_640_found_list = []
    m_empty_response_list = []
    movies_total_list = []

    tv_4k_found_list = []
    tv_1080_found_list = []
    tv_720_found_list = []
    tv_640_found_list = []
    tv_empty_response_list = []
    tv_total_list = []

    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as m_i_i:
        movie_files_results_list = list(csv.reader(m_i_i))
    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_files_results_list = list(csv.reader(t_i_i))

        for res in movie_files_results_list:
            if re.findall(r'[2-9]\d{3}x', res[6]):
                m_4k_found_list.append(res)

            elif re.findall(r'19\d{2}x', res[6]):
                m_1080_found_list.append(res)

            elif re.findall(r'1[0-8]\d{2}x', res[6]):
                m_720_found_list.append(res)

            elif re.findall(r'\d{3}x', res[6]):
                m_640_found_list.append(res)

            else:
                m_empty_response_list.append(+1)
            movies_total_list.append(+1)

        movies_graph_terminal_results = [('4k', float(len(m_4k_found_list))),
                                         ('1080p', float(len(m_1080_found_list))),
                                         ('720p', float(len(m_720_found_list))),
                                         ('640p', float(len(m_640_found_list)))]

        movie_data = [float(len(m_4k_found_list)), float(len(m_1080_found_list)),
                      float(len(m_720_found_list)), float(len(m_640_found_list))]

        for res in tv_files_results_list:
            if re.findall(r'[2-9]\d{3}x', res[6]):
                tv_4k_found_list.append(res)

            elif re.findall(r'19\d{2}x', res[6]):
                tv_1080_found_list.append(res)

            elif re.findall(r'1[0-8]\d{2}x', res[6]):
                tv_720_found_list.append(res)

            elif re.findall(r'\d{3}x', res[6]):
                tv_640_found_list.append(res)

            else:
                tv_empty_response_list.append(+1)
            tv_total_list.append(+1)

        tv_shows_graph_terminal_results = [('4k', float(len(tv_4k_found_list))),
                                           ('1080p', float(len(tv_1080_found_list))),
                                           ('720p', float(len(tv_720_found_list))),
                                           ('640p', float(len(tv_640_found_list)))]

        tv_data = [float(len(tv_4k_found_list)), float(len(tv_1080_found_list)),
                   float(len(tv_720_found_list)), float(len(tv_640_found_list))]

        graph_color_pattern = [IBlu, BCya, Blu, Pur]

        def format_data(percent, all_values):
            absolute = int(percent / 100. * numpy.sum(all_values))
            return '{:.1f}%\n({:d})'.format(percent, absolute)

        labels = ['4k', '1080p', '720p', '640p']
        colors = ['#808B96', '#5C68FC', '#85C1E9', '#A569BD']

        if picture_graph_options_int == 5:
            fig, ax = plt.subplots(figsize=(12, 6), subplot_kw=dict(aspect='equal'))
            wedges, texts, auto_texts = ax.pie(movie_data, autopct=lambda pct: format_data(pct, movie_data),
                                               shadow=True, colors=colors, textprops=dict(color='black'),
                                               pctdistance=1.2, labeldistance=1.0)

            ax.legend(wedges, labels,
                      title='RESOLUTIONS',
                      loc='center right',
                      bbox_to_anchor=(1, 0, 0.5, 1))

            plt.setp(auto_texts, size=8, weight='bold')
            ax.set_title('MOVIE_RESOLUTION_RESULTS')
            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/MOVIE_RESOLUTION_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 5:
            color_movies_graph_terminal_results = vcolor(movies_graph_terminal_results, graph_color_pattern)
            graph = Pyasciigraph()
            for line in graph.graph('MOVIES: RESOLUTION PERCENTAGES: ', color_movies_graph_terminal_results):
                print('\n', line)
            separator_3()

        elif picture_graph_options_int == 6:
            fig, ax = plt.subplots(figsize=(12, 6), subplot_kw=dict(aspect='equal'))
            wedges, texts, auto_texts = ax.pie(tv_data, autopct=lambda pct: format_data(pct, tv_data),
                                               shadow=True, colors=colors, textprops=dict(color='black'),
                                               pctdistance=1.2, labeldistance=1.0)

            ax.legend(wedges, labels,
                      title='RESOLUTIONS',
                      loc='center right',
                      bbox_to_anchor=(1, 0, 0.5, 1))

            plt.setp(auto_texts, size=8, weight='bold')
            ax.set_title('TV_SHOW_RESOLUTION_RESULTS')
            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/TV_RESOLUTION_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 6:
            color_tv_shows_graph_terminal_results = vcolor(tv_shows_graph_terminal_results, graph_color_pattern)
            graph = Pyasciigraph()
            for line in graph.graph('TV SHOWS: RESOLUTION PERCENTAGES: ', color_tv_shows_graph_terminal_results):
                print('\n', line)
            separator_3()


def graph_options_base(picture_graph_options_int, terminal_graph_options_int):
    movie_years_dict = {}
    movie_decades_dict = {}
    tv_years_dict = {}
    tv_decades_amount_dict = {}
    movie_year_totals_dict = {}
    movie_decades_totals_dict = {}
    tv_year_totals_dict = {}
    tv_decades_totals_dict = {}

    graph_color_pattern = [IBlu, BCya, Blu, Pur]

    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as m_i_i:
        movie_files_results_list = list(csv.reader(m_i_i))
    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_files_results_list = list(csv.reader(t_i_i))

        for movie_title_item in movie_files_results_list:
            movie_title_item_year = movie_title_item[10]
            if movie_title_item_year == '[]' or movie_title_item_year == '':
                movie_title_item_year = '0'
            movie_title_item_decade_int = int(str(movie_title_item_year)[:-1] + '0')

            if int(movie_title_item_year) in range(1900, 2100, 1):
                if movie_title_item_year not in movie_years_dict:
                    movie_years_dict[movie_title_item_year] = []
                movie_years_dict[movie_title_item_year].append(movie_title_item_year)

                if movie_title_item_decade_int not in movie_decades_dict:
                    movie_decades_dict[movie_title_item_decade_int] = []
                movie_decades_dict[movie_title_item_decade_int].append(movie_title_item_year)

        for tv_title_item in tv_files_results_list:
            tv_title_item_year = tv_title_item[13]
            if tv_title_item_year == '[]' or tv_title_item_year == '':
                tv_title_item_year = '0'
            tv_title_item_decade_int = int(str(tv_title_item_year)[:-1] + '0')

            if int(tv_title_item_year) in range(1900, 2100, 1):
                if tv_title_item_year not in tv_years_dict:
                    tv_years_dict[tv_title_item_year] = []
                tv_years_dict[tv_title_item_year].append(tv_title_item_year)

                if tv_title_item_decade_int not in tv_decades_amount_dict:
                    tv_decades_amount_dict[tv_title_item_decade_int] = []
                tv_decades_amount_dict[tv_title_item_decade_int].append(tv_title_item_year)

        if picture_graph_options_int == 1:
            for year_values, value in sorted(movie_years_dict.items()):
                movie_year_totals_dict[year_values] = len(value)
            x, y = zip(*sorted(movie_year_totals_dict.items()))

            plt.figure(figsize=[12, 6])
            plt.bar(x, y, color='#A569BD')
            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/MOVIE_YEAR_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 1:
            for movie_year_values, value in sorted(movie_years_dict.items()):
                movie_year_totals_dict[movie_year_values] = len(value)
            movie_data = sorted(movie_year_totals_dict.items())
            movie_years_terminal_graph_list = []

            for key, value in movie_data:
                movie_years_terminal_graph_list.append((str(key), value))

            color_movie_years_terminal_graph_list = vcolor(movie_years_terminal_graph_list, graph_color_pattern)
            graph = Pyasciigraph()

            for line in graph.graph('MOVIES: YEAR AMOUNTS: ', color_movie_years_terminal_graph_list):
                print('\n', line)
            separator_3()

        elif picture_graph_options_int == 2:
            for year_values, value in sorted(tv_years_dict.items()):
                tv_year_totals_dict[year_values] = len(value)
            x, y = zip(*sorted(tv_year_totals_dict.items()))

            plt.figure(figsize=[12, 6])
            plt.bar(x, y, color='#A569BD')
            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/TV_YEAR_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 2:
            for tv_year_values, value in sorted(tv_years_dict.items()):
                tv_year_totals_dict[tv_year_values] = len(value)
            tv_data = sorted(tv_year_totals_dict.items())
            tv_years_terminal_graph_list = []

            for key, value in tv_data:
                tv_years_terminal_graph_list.append((str(key), value))

            color_tv_years_terminal_graph_list = vcolor(tv_years_terminal_graph_list, graph_color_pattern)
            graph = Pyasciigraph()

            for line in graph.graph('TV SHOWS: YEAR AMOUNTS: ', color_tv_years_terminal_graph_list):
                print('\n', line)
            separator_3()

        elif picture_graph_options_int == 3:
            for year_values, value in sorted(movie_decades_dict.items()):
                movie_decades_totals_dict[year_values] = len(value)
            x, y = zip(*movie_decades_totals_dict.items())

            plt.figure(figsize=[12, 6])
            plt.bar(x, y, width=5, color='#A569BD')
            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/MOVIE_DECADE_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 3:
            for movie_year_values, value in sorted(movie_decades_dict.items()):
                movie_decades_totals_dict[movie_year_values] = len(value)
            movie_decades_terminal_graph_list = []

            for key, value in movie_decades_totals_dict.items():
                movie_decades_terminal_graph_list.append((str(key), value))

            color_movie_decades_terminal_graph_list = vcolor(movie_decades_terminal_graph_list, graph_color_pattern)
            graph = Pyasciigraph()

            for line in graph.graph('MOVIES: DECADE AMOUNTS: ', color_movie_decades_terminal_graph_list):
                print('\n', line)
            separator_3()

        elif picture_graph_options_int == 4:
            for year_values, value in sorted(tv_decades_amount_dict.items()):
                tv_decades_totals_dict[year_values] = len(value)
            x, y = zip(*tv_decades_totals_dict.items())

            plt.figure(figsize=[12, 6])
            plt.bar(x, y, width=5, color='#A569BD')
            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/TV_DECADE_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 4:
            for tv_year_values, value in sorted(tv_decades_amount_dict.items()):
                tv_decades_totals_dict[tv_year_values] = len(value)
            tv_decades_terminal_graph_list = []

            for key, value in tv_decades_totals_dict.items():
                tv_decades_terminal_graph_list.append((str(key), value))

            color_tv_decades_terminal_graph_list = vcolor(tv_decades_terminal_graph_list, graph_color_pattern)
            graph = Pyasciigraph()

            for line in graph.graph('TV SHOWS: DECADE AMOUNTS: ', color_tv_decades_terminal_graph_list):
                print('\n', line)
            separator_3()


def launch_media_index():
    print(pyfiglet.figlet_format('MEDIA_INDEX', font='cybermedium'))
    separator_3()

    try:

        global username
        username = input('ENTER YOUR USERNAME (CASE-SENSITIVE): ')
        if username == '':
            separator_3()
            print('USERNAME CANNOT BE LEFT BLANK: ')
            separator_3()
            launch_media_index()
        separator_3()
        username_check_and_folder_creation()

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')
        launch_media_index()


def library_total_amount():
    tv_amounts_list = []
    episode_amounts_list = []
    movie_amounts_list = []

    with open(os.path.expanduser((index_folder + '/MOVIE_VIDEO_FILES_PATHS.csv').format(username)),
              encoding='UTF-8') as m_f_p:
        movie_title_list = list(csv.reader(m_f_p))
    with open(os.path.expanduser((index_folder + '/TV_VIDEO_FILES_PATHS.csv').format(username)),
              encoding='UTF-8') as t_f_p:
        tv_episode_list = list(csv.reader(t_f_p))
    with open(os.path.expanduser((index_folder + '/TV_PLOTS_INDEX.csv').format(username)),
              encoding='UTF-8') as t_p_i:
        tv_show_list = list(csv.reader(t_p_i))

        for counted_movie_title in movie_title_list:
            if not counted_movie_title[0].lower().endswith('.nfo'):
                movie_amounts_list.append(counted_movie_title)

        for counted_tv_title in tv_show_list:
            tv_amounts_list.append(counted_tv_title)

        for episodes in tv_episode_list:
            if not episodes[0].lower().endswith('.nfo'):
                episode_amounts_list.append(+1)

        print('\n', 'TOTAL AMOUNT OF MOVIES: ', '\n')
        print(len(movie_amounts_list))
        separator_3()
        print('\n', 'TOTAL AMOUNT OF TV SHOWS: ', '\n')
        print(len(tv_amounts_list))
        print('\n', '\n', 'TOTAL AMOUNT OF TV EPISODES: ', '\n')
        print(len(episode_amounts_list))
        separator_3()
        print('\n', 'TOTAL AMOUNT OF ITEMS IN MEDIA-LIBRARY: ', '\n')
        print(len(movie_amounts_list) + len(episode_amounts_list))
        separator_3()


def match_similar_strings(a, b):
    return SequenceMatcher(None, a, b).ratio()


def media_index_home():
    print(pyfiglet.figlet_format('MEDIA_INDEX', font='cybermedium'))
    separator_3()

    print('1) ADD / CHANGE DATABASE DIRECTORIES             2) CREATE PATH INDICES', '\n')
    print('3) CREATE / UPDATE MEDIA INFORMATION INDICES     4) COMPARE TWO USERS INFORMATION INDICES', '\n')
    print('5) DISPLAY LIBRARY TOTALS                        6) MEDIA INFORMATION QUERIES', '\n')
    print('7) SORT OPTIONS                                  8) PICTURE GRAPH OPTIONS', '\n')
    print('9) TERMINAL GRAPH OPTIONS                        10) TIME INFORMATION QUERIES', '\n')
    print('11) SAVED SEARCHES')
    separator_2()
    print('0) EXIT MEDIA-INDEX')
    separator_3()

    try:

        lmi_input = input('ENTER #: ')
        separator_3()
        lmi_input_action = int(lmi_input)

        if lmi_input_action == 0:
            exit()

        elif lmi_input_action == 1:

            try:

                print('CONFIRM: ')
                separator_1()
                print('1) CHANGE DATABASE DIRECTORIES                       0) MAIN MENU')
                separator_3()
                db_scan_sub_input = int(input('ENTER #: '))
                separator_3()

                if db_scan_sub_input == 0:
                    media_index_home()

                elif db_scan_sub_input == 1:
                    change_directory_selection()

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
                separator_3()

        elif lmi_input_action == 2:

            try:

                print('CONFIRM: ')
                separator_1()
                print('THIS OPERATION MAY TAKE A LONG TIME (SEVERAL MINUTES FOR LARGE LIBRARIES)')
                separator_2()
                print('1) CONTINUE WITH MEDIA PATH(S) SCAN                  0) MAIN MENU')
                separator_3()
                path_scan_sub_input = int(input('ENTER #: '))
                separator_3()

                if path_scan_sub_input == 0:
                    media_index_home()

                elif path_scan_sub_input == 1:
                    walk_directories_and_create_indices()

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
                separator_3()

        elif lmi_input_action == 3:

            try:

                print('CONFIRM: ')
                separator_1()
                print('THIS OPERATION CAN TAKE A LONG TIME (SEVERAL HOURS FOR LARGE LIBRARIES)')
                separator_2()
                print('1) CONTINUE WITH MEDIA INFORMATION SCAN              0) MAIN MENU')
                separator_3()
                information_scan_sub_input = int(input('ENTER #: '))
                separator_3()

                if information_scan_sub_input == 0:
                    media_index_home()

                elif information_scan_sub_input == 1:
                    create_media_information_indices()

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
                separator_3()

        elif lmi_input_action == 4:

            try:

                print('CONFIRM: ')
                separator_1()
                print('1) COMPARE USER(S) INFORMATION INDICES               0) MAIN MENU')
                separator_3()
                comparison_scan_sub_input = int(input('ENTER #: '))
                separator_3()

                if comparison_scan_sub_input == 0:
                    media_index_home()

                elif comparison_scan_sub_input == 1:
                    select_users_indices_to_compare()

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
                separator_3()

        elif lmi_input_action == 5:
            library_total_amount()

        elif lmi_input_action == 6:
            media_queries_sub_menu()

        elif lmi_input_action == 7:
            sort_options_sub_menu()

        elif lmi_input_action == 8:
            picture_graph_options_sub_menu()

        elif lmi_input_action == 9:
            terminal_graph_options_sub_menu()

        elif lmi_input_action == 10:
            time_queries_sub_menu()

        elif lmi_input_action == 11:
            saved_searches()

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()


def media_queries_sub_menu():
    print(pyfiglet.figlet_format('MEDIA_QUERIES', font='cybermedium'))
    separator_3()

    print('SEARCH FOR TITLES OF:                            1) MOVIES       2) TV SHOWS', '\n')
    print('SEARCH FOR TITLES OF:                            3) EPISODES IN A TV SHOW')
    separator_2()
    print('SEARCH FOR DETAILED INFORMATION OF:              4) MOVIES (BY MOVIE TITLE)', '\n')
    print('SEARCH FOR DETAILED INFORMATION OF:              5) TV SHOWS (BY EPISODE TITLE)')
    separator_2()
    print('                                                 6) SEARCH PLOTS FOR KEYWORD(S)')
    separator_2()
    print('                                                 7) TOTAL NUMBER (#) OF EPISODES IN A TV SHOW')
    separator_2()
    print('0) MAIN MENU')
    separator_3()

    try:

        title_search_type = int(input('ENTER #: '))
        separator_3()

        if title_search_type == 0:
            media_index_home()

        elif title_search_type == 1:
            movie_title_query_input = str(input('QUERY MOVIES: ').lower())
            separator_3()
            search_titles(title_search_type=1, movie_title_query=movie_title_query_input,
                          tv_show_query='')

        elif title_search_type == 2:
            tv_show_query_input = str(input('ENTER SEARCH QUERY (TV SHOWS): ').lower())
            separator_3()
            search_titles(title_search_type=2, movie_title_query='',
                          tv_show_query=tv_show_query_input)

        elif title_search_type == 3:
            tv_show_query_input = str(input('ENTER SEARCH QUERY (TV SHOWS): ').lower())
            separator_3()
            search_titles(title_search_type=3, movie_title_query='',
                          tv_show_query=tv_show_query_input)

        elif title_search_type == 4:
            movie_title_query_input = str(input('ENTER SEARCH QUERY (MOVIES): ').lower())
            separator_3()
            query_movie_information_index(movie_query=movie_title_query_input)

        elif title_search_type == 5:
            tv_episode_query_input = str(input('ENTER SEARCH QUERY (TV SHOWS): ').lower())
            separator_3()
            query_tv_information_index(tv_episode_query=tv_episode_query_input)

        elif title_search_type == 6:

            plot_search_list = []

            try:

                print('SEARCH PLOTS OF:                             1) MOVIES       2) TV SHOW EPISODES', '\n')
                print('                                             3) MOVIES AND TV SHOW EPISODES')
                separator_2()
                print('                                             4) TV SHOW GENERAL OVERVIEW')
                separator_2()
                print('0) MAIN MENU')
                separator_3()

                plot_search_int = int(input('ENTER #: '))
                plot_search_list.append(plot_search_int)
                separator_3()
                plot_search_type_input = plot_search_list[0]

                if int(plot_search_list[0]) == 0:
                    media_index_home()

                else:

                    try:

                        plot_search = input('KEYWORD(S): ')
                        plot_search_list.append(plot_search.lower())
                        separator_3()

                    except (OSError, TypeError, ValueError) as e:
                        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')
                        separator_3()
                plot_search_keywords_input = plot_search_list[1]
                search_plots(plot_search_type=plot_search_type_input, plot_search_keywords=plot_search_keywords_input)

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
                separator_3()

        elif title_search_type == 7:
            total_tv_episodes_in_show_title()

        elif title_search_type == 8:
            time_queries_sub_menu()

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()


def picture_graph_options_sub_menu():
    print(pyfiglet.figlet_format('PICTURE_GRAPHS', font='cybermedium'))
    separator_3()

    print('1) MOVIES (TITLES PER YEAR)                      2) TV SHOWS (TITLES PER YEAR)', '\n')
    print('3) MOVIES (TITLES PER DECADE)                    4) TV SHOWS (TITLES PER DECADE)')
    separator_2()
    print('5) MOVIES (RESOLUTIONS PERCENTAGES)              6) TV SHOWS (RESOLUTIONS PERCENTAGES)')
    separator_2()
    print('7) MOVIES (FILE-TYPE AMOUNTS)                    8) TV SHOWS (FILE-TYPE AMOUNTS)')
    separator_2()
    print('0) MAIN MENU')
    separator_3()

    try:

        picture_graph_options = input('ENTER #: ')
        separator_3()
        picture_graph_options_int = int(picture_graph_options)

        if picture_graph_options_int == 0:
            media_index_home()

        elif 1 <= picture_graph_options_int <= 4:
            graph_options_base(picture_graph_options_int=picture_graph_options_int,
                               terminal_graph_options_int='')

        elif 5 <= picture_graph_options_int <= 6:
            graph_options_advanced(picture_graph_options_int=picture_graph_options_int,
                                   terminal_graph_options_int='')

        elif 7 <= picture_graph_options_int <= 8:
            query_file_type_totals(picture_graph_options_int=picture_graph_options_int,
                                   terminal_graph_options_int='')

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()


def query_file_type_totals(picture_graph_options_int, terminal_graph_options_int):
    movie_extensions_dictionary = {}
    movie_extensions_totals = {}
    tv_extensions_dictionary = {}
    tv_extensions_totals = {}

    graph_color_pattern = [IBlu, BCya, Blu, Pur]

    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as m_i_i:
        movie_files_results_list = list(csv.reader(m_i_i))
    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_files_results_list = list(csv.reader(t_i_i))

        for file_type in movie_files_results_list:
            if ',' not in file_type[5]:

                if file_type[5] not in movie_extensions_dictionary:
                    movie_extensions_dictionary[file_type[5]] = []
                movie_extensions_dictionary[file_type[5]].append(file_type[5])
        movie_file_type_totals = {}

        if picture_graph_options_int == 7:

            for movie_file_type_values, value in sorted(movie_extensions_dictionary.items()):
                movie_file_type_totals[movie_file_type_values] = len(value)
            x, y = zip(*sorted(movie_file_type_totals.items()))

            plt.figure(figsize=[12, 6])
            plt.bar(x, y, width=0.3, color='#A569BD')
            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/MOVIE_FILETYPE_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 7:

            for file_type_values, value in sorted(movie_extensions_dictionary.items()):
                movie_extensions_totals[file_type_values] = len(value)
            file_type_totals_terminal_graph_list = []

            for key, value in movie_extensions_totals.items():
                file_type_totals_terminal_graph_list.append((str(key), value))

            color_file_type_totals_terminal_graph_list = vcolor(file_type_totals_terminal_graph_list,
                                                                graph_color_pattern)
            graph = Pyasciigraph()

            for line in graph.graph('MOVIES: FILE-TYPE AMOUNTS: ', color_file_type_totals_terminal_graph_list):
                print('\n', line)
            separator_3()

        for file_type in tv_files_results_list:
            if ',' not in file_type[5]:
                if file_type[5] not in tv_extensions_dictionary:
                    tv_extensions_dictionary[file_type[5]] = []
                tv_extensions_dictionary[file_type[5]].append(file_type[5])
        tv_file_type_totals = {}

        if picture_graph_options_int == 8:

            for tv_file_type_values, value in sorted(tv_extensions_dictionary.items()):
                tv_file_type_totals[tv_file_type_values] = len(value)
            x, y = zip(*sorted(tv_file_type_totals.items()))

            plt.figure(figsize=[12, 6])
            plt.bar(x, y, width=0.3, color='#A569BD')

            plt_path = os.path.expanduser('~/{0}_MEDIA_INDEX/GRAPHS/TV_FILETYPE_RESULTS_'.format(username) +
                                          date_string + '.png')
            plt.savefig(plt_path)
            print('GRAPH SAVED: ', plt_path)
            separator_3()
            plt.show()

        elif terminal_graph_options_int == 8:

            for file_type_values, value in sorted(tv_extensions_dictionary.items()):
                tv_extensions_totals[file_type_values] = len(value)
            file_type_totals_terminal_graph_list = []

            for key, value in tv_extensions_totals.items():
                file_type_totals_terminal_graph_list.append((str(key), value))

            color_file_type_totals_terminal_graph_list = vcolor(file_type_totals_terminal_graph_list,
                                                                graph_color_pattern)
            graph = Pyasciigraph()

            for line in graph.graph('TV SHOWS: FILE-TYPE AMOUNTS: ', color_file_type_totals_terminal_graph_list):
                print('\n', line)
            separator_3()


def query_movie_information_index(movie_query):
    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as m_i_i:
        mv_files_results_list = csv.reader(m_i_i)

        try:

            for movie_file in mv_files_results_list:
                if str(movie_query.lower()) in str(movie_file[9].lower()):

                    separator_2()
                    print('MOVIE MEDIA-PATH: ', '\n', textwrap.fill(movie_file[0], 100))
                    separator_2()
                    print('MOVIE MEDIA-TYPE: ', '\n', movie_file[1])
                    separator_2()
                    print('MOVIE FOLDER NAME: ', '\n', movie_file[2])
                    separator_2()
                    print('MOVIE FILE-NAME: ', '\n', movie_file[3])
                    separator_2()
                    print('MOVIE FILE-SIZE: ', '\n', movie_file[4], 'MB')
                    separator_2()
                    print('MOVIE FILE-TYPE: ', '\n', movie_file[5])
                    separator_2()
                    print('MOVIE RESOLUTION: ', '\n', movie_file[6])
                    separator_2()
                    print('MOVIE GUESSIT SEARCH TERM: ', '\n', movie_file[7])
                    separator_2()
                    print('MOVIE IMDB ID#: ', '\n', movie_file[8])
                    separator_2()
                    print('MOVIE TITLE: ', '\n', movie_file[9])
                    separator_2()
                    print('MOVIE YEAR: ', '\n', movie_file[10])
                    separator_2()
                    print('MOVIE PLOT: ', '\n', textwrap.fill(movie_file[11], 100))
                    separator_2()
                    print('MOVIE RATING: ', '\n', movie_file[12])
                    separator_2()
                    print('MOVIE RUN-TIME: ', '\n', round((int(movie_file[13]) / 60000), 2), 'Minutes')
                    separator_2()
                    print('MOVIE GENRE(S): ', '\n', movie_file[14])
                    separator_2()
                    print('MOVIE DIRECTOR(S): ', '\n', movie_file[15])
                    separator_2()
                    print('MOVIE SEARCH CONFIDENCE PERCENTAGE: ', '\n', round(float(movie_file[16]), 2), '%')
                    separator_2()

        except (TypeError, ValueError) as e:
            print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID QUERY, PLEASE RETRY')
            separator_3()


def query_tv_information_index(tv_episode_query):
    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_files_results_list = csv.reader(t_i_i)

        try:

            for tv_file in tv_files_results_list:
                if str(tv_episode_query.lower()) in str(tv_file[12].lower()):

                    separator_2()
                    print('TV SHOW MEDIA-PATH: ', '\n', textwrap.fill(tv_file[0], 100))
                    separator_2()
                    print('TV SHOW MEDIA-TYPE: ', '\n', tv_file[1])
                    separator_2()
                    print('TV SHOW FOLDER NAME: ', '\n', tv_file[2])
                    separator_2()
                    print('TV SHOW FILE-NAME: ', '\n', tv_file[3])
                    separator_2()
                    print('TV SHOW FILE-SIZE: ', '\n', tv_file[4], 'MB')
                    separator_2()
                    print('TV SHOW FILE-TYPE: ', '\n', tv_file[5])
                    separator_2()
                    print('TV SHOW RESOLUTION: ', '\n', tv_file[6])
                    separator_2()
                    print('TV SHOW GUESSIT SEARCH TERM: ', '\n', tv_file[7])
                    separator_2()
                    print('TV SHOW IMDB ID#: ', '\n', tv_file[8])
                    separator_2()
                    print('TV SHOW TITLE: ', '\n', tv_file[9])
                    separator_2()
                    print('TV SHOW SEASON #: ', '\n', tv_file[10])
                    separator_2()
                    print('TV SHOW EPISODE #: ', '\n', tv_file[11])
                    separator_2()
                    print('TV SHOW EPISODE TITLE: ', '\n', tv_file[12])
                    separator_2()
                    print('TV SHOW YEAR: ', '\n', tv_file[13])
                    separator_2()
                    print('TV SHOW PLOT: ', '\n', textwrap.fill(tv_file[14], 100))
                    separator_2()
                    print('TV SHOW RATING: ', '\n', tv_file[15])
                    separator_2()
                    print('TV SHOW RUN-TIME: ', '\n', round((int(tv_file[16]) / 60000), 2), 'Minutes')
                    separator_2()
                    print('TV SHOW GENRE(S): ', '\n', tv_file[17])
                    separator_2()
                    print('TV SHOW SEARCH CONFIDENCE PERCENTAGE: ', '\n', round(float(tv_file[18]), 2), '%')
                    separator_2()

        except (TypeError, ValueError) as e:
            print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID QUERY, PLEASE RETRY')
            separator_3()


def saved_searches():
    print(pyfiglet.figlet_format('SAVED_SEARCHES', font='cybermedium'))
    separator_3()

    saved_searches_file = os.path.expanduser((index_folder + '/SEARCH/SAVED_SEARCHES.csv').format(username))
    saved_search_inputs_list = []
    saved_searches_list = []
    search_keywords_list = []

    print('1) VIEW SAVED SEARCH TERMS (GENRE(S), KEYWORD(S))')
    separator_2()
    print('2) ADD A NEW SEARCH TERM')
    separator_2()
    print('3) REMOVE A SEARCH TERM')
    separator_2()
    print('0) MAIN MENU')
    separator_3()

    saved_search_type_input = int(input('ENTER #: '))
    saved_search_inputs_list.append(saved_search_type_input)
    separator_3()

    try:

        if saved_search_inputs_list[0] == 0:
            media_index_home()

        elif saved_search_inputs_list[0] == 1:
            if os.path.isfile(saved_searches_file):

                with open(saved_searches_file, 'r', encoding='UTF-8', newline='') as s_s_f:
                    search_rows = list(csv.reader(s_s_f))

                if int(len(search_rows)) == 0:
                    print('NO SAVED SEARCH TERMS: ')
                    separator_3()
                    saved_searches()

                for enumeration_number, search_terms in enumerate(search_rows):
                    genres = search_terms[0]
                    keywords = search_terms[1]
                    saved_searches_list.append([genres, keywords])
                    print(str(enumeration_number) + ') ', '\n', '\n',
                          'GENRE: ', genres, '\n', 'KEYWORD(S): ', keywords, '\n')

                separator_3()
                print('1) QUERY DATABASE WITH SAVED SEARCH TERM(S): ')
                separator_2()
                print('0) MAIN MENU')
                separator_3()

                saved_search_sub_query_type_input = int(input('ENTER #: '))
                saved_search_inputs_list.append(saved_search_sub_query_type_input)
                separator_3()

                try:

                    if saved_search_inputs_list[1] == 0:
                        media_index_home()

                    elif saved_search_inputs_list[1] == 1:
                        print('SELECT NUMBER (#) FOR GENRE, KEYWORD(S) TO SEARCH: ')
                        separator_3()
                        saved_search_sub_query_input = int(input('ENTER #: '))
                        search_term = saved_searches_list[saved_search_sub_query_input]

                        for words in search_term[1].split(' '):
                            words = words.strip()
                            search_keywords_list.append(words)

                        for found_search_terms in search_keywords_list:
                            separator_3()
                            print('QUERYING INFORMATION FOR SELECTED KEYWORD(S): ', found_search_terms)
                            separator_3()
                            search_plots(plot_search_type=3, plot_search_keywords=found_search_terms)
                        saved_searches()

                except (TypeError, ValueError) as i_e:
                    print('\n', 'INPUT ERROR: ', i_e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
                    separator_3()

            else:

                with open(saved_searches_file, 'w', encoding='UTF-8', newline='') as _:
                    pass

                print('NO SAVED SEARCH TERMS: ')
                separator_3()
                saved_searches()

        elif saved_search_inputs_list[0] == 2:
            print('1) ADD SEARCH TERM: ')
            separator_2()
            print('0) MAIN MENU')
            separator_3()
            addition_confirmation_number = int(input('ENTER #: '))
            separator_3()

            if addition_confirmation_number == 1:
                print('SELECT TITLE FOR GENRE, ADD KEYWORD(S) FOR SEARCH TERM(S))')
                separator_2()

                new_genre = str(input('ENTER TITLE FOR NEW GENRE: '))
                separator_2()
                new_search_term = str(input('ENTER KEYWORD(S) (SEPARATE KEYWORD(S) BY SPACES, NOT COMMAS): ')).lower()
                separator_3()

                saved_searches_list.append([new_genre, new_search_term])

                with open(saved_searches_file, 'a', encoding='UTF-8', newline='') as s_s_f:
                    csv_writer = csv.writer(s_s_f)
                    for user_data in saved_searches_list:
                        csv_writer.writerow(user_data)

                saved_searches()

            else:
                saved_searches()

        elif saved_search_inputs_list[0] == 3:
            if os.path.isfile(saved_searches_file):

                with open(saved_searches_file, 'r', encoding='UTF-8', newline='') as s_s_f:
                    search_rows = list(csv.reader(s_s_f))

                if int(len(search_rows)) == 0:
                    print('NO SAVED SEARCH TERMS: ')
                    separator_3()
                    saved_searches()

                for enumeration_number, search_terms in enumerate(search_rows):
                    genres = search_terms[0]
                    keywords = search_terms[1]
                    saved_searches_list.append([genres, keywords])
                    print(str(enumeration_number) + ') ', '\n', '\n',
                          'GENRE: ', genres, '\n', 'KEYWORD(S): ', keywords, '\n')
                separator_3()

                print('1) REMOVE SEARCH TERM: ')
                separator_2()
                print('0) MAIN MENU')
                separator_3()
                removal_confirmation_number = int(input('ENTER #: '))
                separator_3()

                if removal_confirmation_number == 1:
                    separator_3()
                    print('SELECT NUMBER OF SEARCH TERM TO REMOVE: ', '\n')
                    search_term_to_remove_number = int(input('ENTER #: '))
                    separator_3()
                    print('SEARCH TERM REMOVED: ')
                    separator_3()
                    saved_searches_list.remove(saved_searches_list[search_term_to_remove_number])

                    with open(saved_searches_file, 'w', encoding='UTF-8', newline='') as s_s_f:
                        csv_writer = csv.writer(s_s_f)
                        for user_data in saved_searches_list:
                            csv_writer.writerow(user_data)

                else:
                    saved_searches()

            else:
                with open(saved_searches_file, 'w', encoding='UTF-8', newline='') as _:
                    pass

                print('NO SAVED SEARCH TERMS: ')
                separator_3()
                saved_searches()

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()


def search_plots(plot_search_type, plot_search_keywords):
    plots_list = []

    with open(os.path.expanduser(
            (index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)), encoding='UTF-8') as m_i_i:
        movie_files_results_list = list(csv.reader(m_i_i))
    with open(os.path.expanduser(
            (index_folder + '/TV_INFORMATION_INDEX.csv').format(username)), encoding='UTF-8') as t_i_i:
        tv_files_results_list = list(csv.reader(t_i_i))
    with open(os.path.expanduser(
            (index_folder + '/TV_PLOTS_INDEX.csv').format(username)), encoding='UTF-8') as t_p_i:
        tv_plots_list = list(csv.reader(t_p_i))

        if int(plot_search_type) == 1:
            for plot in movie_files_results_list:
                plots_list.append('MOVIE' + ' - ' + plot[9] + ' - ' + plot[11])

            for items in plots_list:
                if plot_search_keywords.lower() in items.lower():
                    print('\n', textwrap.fill(items, 100))
            separator_3()

        elif int(plot_search_type) == 2:
            for plot in tv_files_results_list:
                plots_list.append('TV SHOW' + ' - ' + plot[9] + ' - ' + plot[12] + ' - ' + plot[14])

            for items in plots_list:
                if plot_search_keywords.lower() in items.lower():
                    print('\n', textwrap.fill(items, 100))
            separator_3()

        elif int(plot_search_type) == 3:
            for plot in movie_files_results_list:
                plots_list.append('MOVIE' + ' - ' + plot[9] + ' - ' + plot[11])

            for plot in tv_files_results_list:
                plots_list.append('TV SHOW' + ' - ' + plot[9] + ' - ' + plot[12] + ' - ' + plot[14])

            for items in plots_list:
                if plot_search_keywords.lower() in items.lower():
                    print('\n', textwrap.fill(items, 100))
            separator_3()

        elif int(plot_search_type) == 4:
            for plot in tv_plots_list:
                plots_list.append('TV SHOW' + ' - ' + plot[0] + ' - ' + plot[1])

            for items in plots_list:
                if plot_search_keywords.lower() in items.lower():
                    print('\n', textwrap.fill(items, 100))
            separator_3()


def search_titles(title_search_type, movie_title_query, tv_show_query):
    episode_information_list = []
    episode_information_search_list = []
    episode_folder_titles_dictionary = {}
    episode_folder_titles_list = []

    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as m_i_i:
        movie_files_results_list = list(csv.reader(m_i_i))
    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_files_results_list = csv.reader(t_i_i)

        if title_search_type == 1:

            try:

                print('SEARCH RESULTS: ')
                separator_1()
                print('MOVIES: ', '\n')

                for movie_search_result in movie_files_results_list:
                    search_info = movie_search_result[9]

                    if movie_title_query.lower() in search_info.lower():
                        print(search_info)
                separator_3()

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')
                separator_3()

        elif title_search_type == 2:

            try:

                tv_search_dict = {}
                print('SEARCH RESULTS: ')
                separator_1()
                print('TV SHOWS: ', '\n')

                for tv_search_result in tv_files_results_list:

                    search_info = tv_search_result[9]
                    if search_info not in tv_search_dict:
                        tv_search_dict[search_info] = search_info

                for found_tv_show_titles in tv_search_dict:
                    if tv_show_query.lower() in found_tv_show_titles.lower():
                        print(found_tv_show_titles)
                separator_3()

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')
                separator_3()

        elif title_search_type == 3:

            try:

                for tv_file in tv_files_results_list:
                    tv_folder_key = tv_file[2]
                    tv_title_key = tv_file[9]
                    tv_episode_name_key = tv_file[12]

                    if tv_show_query.lower() in tv_title_key.lower():

                        if str(tv_episode_name_key) == '':
                            tv_episode_name_key = 'MEDIA_INDEX - NO EPISODE TITLE'
                        episode_information_list.append([tv_title_key, tv_episode_name_key])

                        if tv_folder_key not in episode_folder_titles_dictionary:
                            episode_folder_titles_dictionary[tv_folder_key] = {}
                            episode_folder_titles_dictionary[tv_folder_key]['EPISODES'] = []
                        episode_folder_titles_dictionary[tv_folder_key]['EPISODES'].append(tv_episode_name_key)

                for enumeration_number, found_episodes in enumerate(episode_information_list):
                    found_tv_folder_key = found_episodes[0]
                    found_tv_episode_name_key = found_episodes[1]
                    episode_information_search_list.append([(str(enumeration_number) + ') '),
                                                            (str(found_tv_folder_key) + ' - '),
                                                            found_tv_episode_name_key])

                empty_results_list = []
                print('TV SHOWS FOUND: ')
                separator_1()

                for found_tv_shows in episode_folder_titles_dictionary.keys():
                    episode_folder_titles_list.append(found_tv_shows)

                for show_titles in episode_folder_titles_list:
                    empty_results_list.append(show_titles)
                    print('-', show_titles)

                separator_3()
                print('EPISODES FOUND: ')
                separator_1()

                for search_results in episode_information_search_list:
                    print(''.join(search_results))

                if len(empty_results_list) >= 1:

                    separator_2()
                    print('DETAILED EPISODE INFORMATION AVAILABLE: ')
                    separator_1()
                    print('0) MAIN MENU                                 1) QUERY AN EPISODES INFORMATION')
                    separator_3()

                    try:

                        title_search_sub_query_input = int(input('ENTER #: '))
                        separator_3()

                        if title_search_sub_query_input == 0:
                            media_index_home()

                        elif title_search_sub_query_input == 1:

                            episode_sub_query_input = int(input('ENTER EPISODE NUMBER (#): '))
                            episode_to_query = str(episode_information_search_list[episode_sub_query_input][2])
                            episode_to_query_lower = episode_to_query.lower()
                            separator_3()

                            print('QUERYING INFORMATION FOR EPISODE TITLED: ', episode_to_query)
                            separator_2()
                            query_tv_information_index(tv_episode_query=episode_to_query_lower)

                    except (TypeError, ValueError) as e:
                        print('\n', 'INPUT ERROR: ', e, '\n', '\n',
                              'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
                        separator_3()

                else:
                    separator_3()
                    media_index_home()

            except (TypeError, ValueError) as e:
                print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')
                separator_3()


def select_users_indices_to_compare():
    try:

        print('\n', 'SELECT THE MOVIE_INFORMATION_INDICES TO COMPARE: ')
        separator_3()

        print('SELECT USER MOVIE INFORMATION INDEX: ')
        m_0 = tk_gui_file_selection_window()

        print('SELECT COMPARISON MOVIE INFORMATION INDEX: ')
        m_1 = tk_gui_file_selection_window()

        print('SELECT USER TV INFORMATION INDEX: ')
        t_0 = tk_gui_file_selection_window()

        print('SELECT COMPARISON TV INFORMATION INDEX: ')
        t_1 = tk_gui_file_selection_window()
        separator_3()

        with open(m_0, 'r', encoding='UTF-8') as movies_0, open(m_1, 'r', encoding='UTF-8') as movies_1:
            user_movie_results = movies_0.readlines()
            comparison_movie_results = movies_1.readlines()

            with open(os.path.expanduser(
                    (index_folder + '/FILES/MOVIE_COMPARISON_INDEX.csv').format(username)),
                    'w', encoding='UTF-8', newline='') as outFile_m:
                for line in compare_results(user_movie_results, comparison_movie_results):
                    outFile_m.write(line)

        with open(t_0, 'r', encoding='UTF-8') as tv_0, open(t_1, 'r', encoding='UTF-8') as tv_1:
            user_tv_results = tv_0.readlines()
            comparison_tv_results = tv_1.readlines()

            with open(os.path.expanduser(
                    (index_folder + '/FILES/TV_COMPARISON_INDEX.csv').format(username)),
                    'w', encoding='UTF-8', newline='') as outFile_t:
                for line in compare_results(user_tv_results, comparison_tv_results):
                    outFile_t.write(line)

    except (OSError, TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')
        separator_3()

    print('COMPLETE: COMPARISON FILE(S) CAN BE FOUND IN THE USER MEDIA-INDEX FOLDER, FILES SUB-FOLDER')
    separator_3()


def separator_1():
    print('-' * 100)


def separator_2():
    for items in '\n', '-' * 100:
        print(items)


def separator_3():
    for items in '\n', '-' * 100, '\n':
        print(items)


def sort_function_base(sort_options_int):
    movie_info_list = []
    tv_info_list = []

    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as m_i_i:
        movie_files_results_list = list(csv.reader(m_i_i))

    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_files_results_list = list(csv.reader(t_i_i))

        for movie_info in movie_files_results_list:
            movie_title = movie_info[9]
            movie_size = movie_info[4]
            movie_time = movie_info[13]

            if movie_title == '[]' or movie_title == '':
                movie_title = str('NO MOVIE TITLE')
            if movie_size == '[]' or movie_size == '':
                movie_size = str('0')
            if movie_time == '[]' or movie_time == '':
                movie_time = str('0')

            movie_time_total_readable_minutes = round(int(movie_time) // 60000, 2)
            movie_info_list.append([movie_title, float(movie_size), float(movie_time_total_readable_minutes)])

        for tv_show_info in tv_files_results_list:
            tv_show_title = tv_show_info[9]
            episode_size = tv_show_info[4]
            episode_title = tv_show_info[12]
            episode_time = tv_show_info[16]

            if tv_show_title == '[]' or tv_show_title == '':
                tv_show_title = str('NO TV SHOW TITLE')
            if episode_size == '' or episode_size == '':
                episode_size = str('0')
            if episode_title == '[]' or episode_title == '':
                episode_title = str('NO TV EPISODE TITLE')
            if episode_time == '[]' or episode_time == '':
                episode_time = str('0')

            tv_time_total_readable_minutes = round(int(episode_time) / 60000, 2)
            tv_info_list.append([tv_show_title, episode_title, float(episode_size),
                                 float(tv_time_total_readable_minutes)])

        movies_sorted_by_size = sorted(movie_info_list, key=lambda x: x[1])
        movies_sorted_by_size_r = sorted(movie_info_list, key=lambda x: x[1], reverse=True)
        movies_sorted_by_time = sorted(movie_info_list, key=lambda x: x[2])
        movies_sorted_by_time_r = sorted(movie_info_list, key=lambda x: x[2], reverse=True)
        tv_shows_sorted_by_size = sorted(tv_info_list, key=lambda x: x[2])
        tv_shows_sorted_by_size_r = sorted(tv_info_list, key=lambda x: x[2], reverse=True)
        tv_shows_sorted_by_time = sorted(tv_info_list, key=lambda x: x[3])
        tv_shows_sorted_by_time_r = sorted(tv_info_list, key=lambda x: x[3], reverse=True)

        if sort_options_int == 1:
            for movie_sizes in movies_sorted_by_size:
                print('\n', movie_sizes[0], '-', movie_sizes[1], ': MB')
            separator_3()

        elif sort_options_int == 2:
            for movie_sizes in movies_sorted_by_size_r:
                print('\n', movie_sizes[0], '-', movie_sizes[1], ': MB')
            separator_3()

        elif sort_options_int == 3:
            for movie_run_times in movies_sorted_by_time:
                print('\n', movie_run_times[0], '-', movie_run_times[2], ': Minutes')
            separator_3()

        elif sort_options_int == 4:
            for movie_run_times in movies_sorted_by_time_r:
                print('\n', movie_run_times[0], '-', movie_run_times[2], ': Minutes')
            separator_3()

        elif sort_options_int == 5:
            for episode_sizes in tv_shows_sorted_by_size:
                print('\n', episode_sizes[0], '-', episode_sizes[1], '-', episode_sizes[2], ': MB')
            separator_3()

        elif sort_options_int == 6:
            for episode_sizes in tv_shows_sorted_by_size_r:
                print('\n', episode_sizes[0], '-', episode_sizes[1], '-', episode_sizes[2], ': MB')
            separator_3()

        elif sort_options_int == 7:
            for episode_run_times in tv_shows_sorted_by_time:
                print('\n', episode_run_times[0], '-', episode_run_times[1], '-', episode_run_times[3], ': Minutes')
            separator_3()

        elif sort_options_int == 8:
            for episode_run_times in tv_shows_sorted_by_time_r:
                print('\n', episode_run_times[0], '-', episode_run_times[1], '-', episode_run_times[3], ': Minutes')
            separator_3()


def sort_function_for_tv_episodes(sort_options_int):
    tv_amounts_list = []
    tv_show_episodes_found_list = []
    tv_show_found_dict = {}
    tv_show_count_found_dict = {}
    tv_show_run_times_total_list = []
    tv_show_file_sizes_total_list = []

    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_results_list = list(csv.reader(t_i_i))

        for tv_title in tv_results_list:
            tv_show_title = tv_title[9]
            if tv_show_title == '[]' or tv_show_title == '':
                tv_show_title = str('NO TV SHOW TITLE')
            tv_amounts_list.append(tv_show_title)
            if tv_show_title not in tv_show_found_dict:
                tv_show_found_dict[tv_show_title] = {}
                tv_show_found_dict[tv_show_title]['RUN-TIMES'] = []
                tv_show_found_dict[tv_show_title]['FILE-SIZES'] = []

            tv_run_times = tv_title[16]
            tv_file_sizes = tv_title[4]

            if tv_run_times == '':
                tv_run_times = 0
            if tv_file_sizes == '':
                tv_file_sizes = 0

            tv_show_found_dict[tv_show_title]['RUN-TIMES'].append(float(tv_run_times))
            tv_show_found_dict[tv_show_title]['FILE-SIZES'].append(float(tv_file_sizes))

        for found_tv_title in tv_amounts_list:
            tv_show_episodes_found_list.append(found_tv_title)
            tv_show_count_found_dict[found_tv_title] = tv_show_episodes_found_list.count(found_tv_title)

        for tv_show_keys, tv_show_values in tv_show_found_dict.items():
            show_run_time_total = sum(tv_show_values['RUN-TIMES'])
            show_run_time_total_seconds = show_run_time_total / 1000
            show_run_time_total_minutes = round(show_run_time_total_seconds / 60, 2)
            tv_show_run_times_total_list.append([tv_show_keys, show_run_time_total_minutes])

        for tv_show_keys, tv_show_values in tv_show_found_dict.items():
            show_file_size_total = sum(tv_show_values['FILE-SIZES'])
            tv_show_file_sizes_total_list.append([tv_show_keys, round(show_file_size_total, 2)])

        episode_titles_a = sorted(tv_show_count_found_dict.items(), key=lambda kv: kv[0])
        episode_titles_d = sorted(tv_show_count_found_dict.items(), key=lambda kv: kv[0], reverse=True)
        episode_amount_a = sorted(tv_show_count_found_dict.items(), key=lambda kv: kv[1])
        episode_amount_d = sorted(tv_show_count_found_dict.items(), key=lambda kv: kv[1], reverse=True)
        episode_times_a = sorted(tv_show_run_times_total_list, key=lambda x: x[1])
        episode_times_d = sorted(tv_show_run_times_total_list, key=lambda x: x[1], reverse=True)
        episode_sizes_a = sorted(tv_show_file_sizes_total_list, key=lambda x: x[1])
        episode_sizes_d = sorted(tv_show_file_sizes_total_list, key=lambda x: x[1], reverse=True)

        if sort_options_int == 9:
            for item in episode_sizes_a:
                print('\n', item[0], '-', item[1], ': MB Total')
            separator_3()

        elif sort_options_int == 10:
            for item in episode_sizes_d:
                print('\n', item[0], '-', item[1], ': MB Total')
            separator_3()

        elif sort_options_int == 11:
            for item in episode_times_a:
                print('\n', item[0], '-', item[1], ': Minutes Total')
            separator_3()

        elif sort_options_int == 12:
            for item in episode_times_d:
                print('\n', item[0], '-', item[1], ': Minutes Total')
            separator_3()

        elif sort_options_int == 13:
            for item in episode_titles_a:
                print('\n', item[0], '-', item[1], ': Episodes')
            separator_3()

        elif sort_options_int == 14:
            for item in episode_titles_d:
                print('\n', item[0], '-', item[1], ': Episodes')
            separator_3()

        elif sort_options_int == 15:
            for item in episode_amount_a:
                print('\n', item[0], '-', item[1], ': Episodes')
            separator_3()

        elif sort_options_int == 16:
            for item in episode_amount_d:
                print('\n', item[0], '-', item[1], ': Episodes')
            separator_3()


def sort_options_sub_menu():
    print(pyfiglet.figlet_format('SORT_OPTIONS', font='cybermedium'))
    separator_3()

    print('SORT MOVIES BY:                      SIZES:      1) ASCENDING    2) DESCENDING', '\n')
    print('                                     TIMES:      3) ASCENDING    4) DESCENDING')
    separator_2()
    print('SORT ALL TV EPISODES BY:             SIZES:      5) ASCENDING    6) DESCENDING', '\n')
    print('                                     TIMES:      7) ASCENDING    8) DESCENDING')
    separator_2()
    print('SORT TV SHOW TOTALS BY:              SIZES:      9) ASCENDING    10) DESCENDING', '\n')
    print('                                     TIMES:      11) ASCENDING   12) DESCENDING')
    separator_2()
    print('SORT NUMBER (#) OF TV EPISODES BY:   TITLES:     13) ASCENDING   14) DESCENDING', '\n')
    print('                                     AMOUNT:     15) ASCENDING   16) DESCENDING')
    separator_2()

    print('0) MAIN MENU')
    separator_3()

    try:

        sort_input = input('ENTER #: ')
        separator_3()
        sort_options_int = int(sort_input)

        if sort_options_int == 0:
            media_index_home()

        elif 1 <= sort_options_int <= 8:
            sort_function_base(sort_options_int=sort_options_int)

        elif 9 <= sort_options_int <= 16:
            sort_function_for_tv_episodes(sort_options_int=sort_options_int)

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()


def terminal_graph_options_sub_menu():
    print(pyfiglet.figlet_format('TERMINAL_GRAPHS', font='cybermedium'))
    separator_3()

    print('1) MOVIES (TITLES PER YEAR)                      2) TV SHOWS (TITLES PER YEAR)', '\n')
    print('3) MOVIES (TITLES PER DECADE)                    4) TV SHOWS (TITLES PER DECADE)')
    separator_2()
    print('5) MOVIES (RESOLUTIONS PERCENTAGES)              6) TV SHOWS (RESOLUTIONS PERCENTAGES)')
    separator_2()
    print('7) MOVIES (FILE-TYPE AMOUNTS)                    8) TV SHOWS (FILE-TYPE AMOUNTS)')
    separator_2()
    print('0) MAIN MENU')
    separator_3()

    try:

        terminal_graph_options = input('ENTER #: ')
        separator_3()
        terminal_graph_options_int = int(terminal_graph_options)

        if terminal_graph_options_int == 0:
            media_index_home()

        elif 1 <= terminal_graph_options_int <= 4:
            graph_options_base(picture_graph_options_int='',
                               terminal_graph_options_int=terminal_graph_options_int)

        elif 5 <= terminal_graph_options_int <= 6:
            graph_options_advanced(picture_graph_options_int='',
                                   terminal_graph_options_int=terminal_graph_options_int)

        elif 7 <= terminal_graph_options_int <= 8:
            query_file_type_totals(picture_graph_options_int='',
                                   terminal_graph_options_int=terminal_graph_options_int)

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()


def time_queries_sub_menu():
    print(pyfiglet.figlet_format('TIME_QUERIES', font='cybermedium'))
    separator_3()

    movie_times_list = []
    tv_times_list = []
    all_media_times_list = []
    time_queries_input_list = []

    try:

        print('                                                 1) QUERY DURATION INFORMATION FOR MOVIES', '\n')
        print('                                                 2) QUERY DURATION INFORMATION FOR TV SHOWS')
        separator_2()
        print('                                                 3) QUERY DURATION INFORMATION FOR ALL MEDIA')
        separator_2()
        print('0) MAIN MENU')
        separator_3()

        time_queries_input = input('ENTER #: ')
        separator_3()
        time_queries_input_int = int(time_queries_input)
        time_queries_input_list.append(time_queries_input_int)

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()

    with open(os.path.expanduser((index_folder + '/MOVIE_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as m_i_i:
        movie_files_results_list = csv.reader(m_i_i)

        for movie_times in movie_files_results_list:
            movie_times_list.append(movie_times[13])
            all_media_times_list.append(movie_times[13])

    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_files_results_list = csv.reader(t_i_i)

        for tv_show_times in tv_files_results_list:
            tv_times_list.append(tv_show_times[16])
            all_media_times_list.append(tv_show_times[16])

    movie_times_total = 0
    tv_times_total = 0

    for found_movie_times in movie_times_list:
        stripped_movie_time = found_movie_times.split('.')[-1]
        if stripped_movie_time == '':
            stripped_movie_time = 0

        movie_times_total = movie_times_total + int(stripped_movie_time)
    movie_times_total_readable_minutes = movie_times_total // 60000
    movie_times_total_readable_hours = movie_times_total_readable_minutes // 60
    movie_times_total_readable_years = movie_times_total_readable_hours / 8760
    rounded_movie_times_total_readable_years = round(movie_times_total_readable_years, 2)

    for found_tv_times in tv_times_list:
        stripped_tv_time = found_tv_times.split('.')[-1]
        if stripped_tv_time == '':
            stripped_tv_time = 0

        tv_times_total = tv_times_total + int(stripped_tv_time)
    tv_times_total_readable_minutes = tv_times_total // 60000
    tv_times_total_readable_hours = tv_times_total_readable_minutes // 60
    tv_times_total_readable_years = tv_times_total_readable_hours / 8760
    rounded_tv_times_total_readable_years = round(tv_times_total_readable_years, 2)

    all_media_times_total = int(movie_times_total) + int(tv_times_total)
    all_times_total_readable_minutes = all_media_times_total // 60000
    all_times_total_readable_hours = all_times_total_readable_minutes // 60
    all_times_total_readable_years = all_times_total_readable_hours / 8760
    rounded_all_times_total_readable_years = round(all_times_total_readable_years, 2)

    try:

        if int(time_queries_input_list[0]) == 0:
            media_index_home()

        elif int(time_queries_input_list[0]) == 1:

            print('TOTAL DURATION FOR ALL MOVIES (IN MINUTES): ', movie_times_total_readable_minutes)
            separator_1()
            print('TOTAL DURATION FOR ALL MOVIES (IN HOURS): ', movie_times_total_readable_hours)
            separator_2()
            print('TOTAL DURATION FOR ALL MOVIES (IN YEARS): ', rounded_movie_times_total_readable_years)
            separator_3()

        elif int(time_queries_input_list[0]) == 2:

            print('TOTAL DURATION FOR ALL TV SHOWS (IN MINUTES): ', tv_times_total_readable_minutes)
            separator_1()
            print('TOTAL DURATION FOR ALL TV SHOWS (IN HOURS): ', tv_times_total_readable_hours)
            separator_2()
            print('TOTAL DURATION FOR ALL TV SHOWS (IN YEARS): ', rounded_tv_times_total_readable_years)
            separator_3()

        elif int(time_queries_input_list[0]) == 3:

            print('TOTAL DURATION FOR ALL MOVIES (IN MINUTES): ', movie_times_total_readable_minutes)
            separator_1()
            print('TOTAL DURATION FOR ALL MOVIES (IN HOURS): ', movie_times_total_readable_hours)
            separator_2()
            print('TOTAL DURATION FOR ALL MOVIES (IN YEARS): ', rounded_movie_times_total_readable_years)
            separator_3()
            print('TOTAL DURATION FOR ALL TV SHOWS (IN MINUTES): ', tv_times_total_readable_minutes)
            separator_1()
            print('TOTAL DURATION FOR ALL TV SHOWS (IN HOURS): ', tv_times_total_readable_hours)
            separator_2()
            print('TOTAL DURATION FOR ALL TV SHOWS (IN YEARS): ', rounded_tv_times_total_readable_years)
            separator_3()
            print('TOTAL DURATION FOR ALL MEDIA (IN MINUTES): ', all_times_total_readable_minutes)
            separator_1()
            print('TOTAL DURATION FOR ALL MEDIA (IN HOURS): ', all_times_total_readable_hours)
            separator_2()
            print('TOTAL DURATION FOR ALL MEDIA (IN YEARS): ', rounded_all_times_total_readable_years)
            separator_3()

    except (TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'PLEASE RETRY YOUR SELECTION USING THE NUMBER KEYS')
        separator_3()


def tk_gui_file_browser_window():
    root = Tk()
    root.withdraw()
    root.update()
    selected_directory = filedialog.askdirectory()
    root.destroy()
    return selected_directory


def tk_gui_file_selection_window():
    root = Tk()
    root.withdraw()
    root.update()
    selected_file = filedialog.askopenfilename()
    root.destroy()
    return selected_file


def total_tv_episodes_in_show_title():
    total_query_action_list = []
    tv_amounts = []
    tv_show_episodes_found = []
    tv_show_found = {}

    with open(os.path.expanduser((index_folder + '/TV_INFORMATION_INDEX.csv').format(username)),
              encoding='UTF-8') as t_i_i:
        tv_results_list = list(csv.reader(t_i_i))

        try:

            tv_total_query_action = input('ENTER TV SHOW TITLE: ')
            separator_3()
            total_query_action_list.append(tv_total_query_action.lower())

        except (OSError, TypeError, ValueError) as e:
            print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')

        for tv_title in tv_results_list:
            tv_amounts.append(tv_title[9])

        for found_tv_title in tv_amounts:
            if total_query_action_list[0] in found_tv_title.lower():
                tv_show_episodes_found.append(found_tv_title)
                tv_show_found[found_tv_title] = tv_show_episodes_found.count(found_tv_title)

        for episode in tv_show_found.items():
            print('TITLE NAME: NUMBER (#) OF EPISODES: ', '\n', episode)
            separator_3()
        print('NUMBER (#) OF EPISODES TOTAL: ', sum(tv_show_found.values()))
        separator_3()


def username_check_and_folder_creation():
    try:

        global movie_dir_input, tv_dir_input, movie_alt_dir_input, tv_alt_dir_input
        user_info_file = os.path.expanduser((index_folder + '/{0}_USER_INFO.json').format(username))

        if os.path.isfile(user_info_file):
            with open(user_info_file) as u_i_f:
                user_data = json.load(u_i_f)
                _ = user_data['user:']
                movie_dir_input = user_data['movie_dir:']
                tv_dir_input = user_data['tv_dir:']
                movie_alt_dir_input = user_data['movie_alt_dir:']
                tv_alt_dir_input = user_data['tv_alt_dir:']

        else:
            os.makedirs(os.path.expanduser((index_folder + '/').format(username)), exist_ok=True)
            os.makedirs(os.path.expanduser((index_folder + '/FILES').format(username)), exist_ok=True)
            os.makedirs(os.path.expanduser((index_folder + '/GRAPHS').format(username)), exist_ok=True)
            os.makedirs(os.path.expanduser((index_folder + '/SEARCH').format(username)), exist_ok=True)
            directory_selection()

    except (OSError, TypeError, ValueError) as e:
        print('\n', 'INPUT ERROR: ', e, '\n', '\n', 'INVALID INPUT, PLEASE RETRY')
        separator_3()
        main()


def walk_directories_and_create_indices():
    movie_video_files_results = []

    media_folders_to_skip = 'extras', 'featurettes', 'special features'

    path_scan_start = time.time()

    if movie_dir_input != '':
        for root, dirs, files in os.walk(movie_dir_input):
            directory = str(pathlib.Path(root).as_posix())
            if not directory.rsplit('/')[-1].lower() in media_folders_to_skip:
                for movie_file in sorted(files):
                    if movie_file.lower().endswith(extensions):
                        movie_video_files_results.append([(pathlib.Path(root) / movie_file).as_posix()])

    if movie_alt_dir_input != '':
        for listed_alternate_movie_directories in movie_alt_dir_input:
            for root, dirs, files in os.walk(listed_alternate_movie_directories):
                directory = str(pathlib.Path(root).as_posix())
                if not directory.rsplit('/')[-1].lower() in media_folders_to_skip:
                    for alt_movie_file in sorted(files):
                        if alt_movie_file.lower().endswith(extensions):
                            movie_video_files_results.append([(pathlib.Path(root) / alt_movie_file).as_posix()])

    with open(os.path.expanduser((index_folder + '/MOVIE_VIDEO_FILES_PATHS.csv').format(username)), 'w',
              encoding='UTF-8', newline='') as m_f_p:
        csv_writer = csv.writer(m_f_p)
        for movie_row in sorted(movie_video_files_results):
            csv_writer.writerow(movie_row)

    tv_show_video_files_results = []

    if tv_dir_input != '':
        for root, dirs, files in os.walk(tv_dir_input):
            directory = str(pathlib.Path(root).as_posix())
            if not directory.rsplit('/')[-1].lower() in media_folders_to_skip:
                for tv_file in sorted(files):
                    if tv_file.lower().endswith(extensions):
                        tv_show_video_files_results.append([(pathlib.Path(root) / tv_file).as_posix()])

    if tv_alt_dir_input != '':
        for listed_alternate_tv_directories in tv_alt_dir_input:
            for root, dirs, files in os.walk(listed_alternate_tv_directories):
                directory = str(pathlib.Path(root).as_posix())
                if not directory.rsplit('/')[-1].lower() in media_folders_to_skip:
                    for alt_tv_file in sorted(files):
                        if alt_tv_file.lower().endswith(extensions):
                            tv_show_video_files_results.append([(pathlib.Path(root) / alt_tv_file).as_posix()])

    with open(os.path.expanduser((index_folder + '/TV_VIDEO_FILES_PATHS.csv').format(username)), 'w',
              encoding='UTF-8', newline='') as t_f_p:
        csv_writer = csv.writer(t_f_p)
        for tv_row in sorted(tv_show_video_files_results):
            csv_writer.writerow(tv_row)

    path_scan_end = time.time()
    readable_path_scan_time = round(path_scan_end - path_scan_start, 2)
    print('MEDIA PATHS SCAN COMPLETE - TIME ELAPSED: ', readable_path_scan_time, 'Seconds')
    separator_3()


if __name__ == '__main__':
    main()
