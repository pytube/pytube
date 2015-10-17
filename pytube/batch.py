#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pytube import YouTube

def batch_download_by_url_list(url_list, extension='mp4', resolution='highest', path='.'):
	'''Download videos by url list

	:param [str] url_list:
		A list of url linked to the videos
	:param str extension:
		The desired file extention. (e.g. mp4, flv)
		Take mp4 as the default value
	:param str resolution:
		The desired video broadcasting standard. (e.g. 720p, 1080p, highest, lowest)
		By choosing highest/lowest, the program would choose videio with the highest/lowest resolusion
		Take the highest resolution as the default choice
	:param str path:
		The destination output directory
	'''
	for url in url_list:
		yt = YouTube(url)
		if(resolution == 'highest' or resolution == 'lowest'):
			video_list = yt.filter(extension)
			if(len(video_list) == 0):
				raise DoesNotExist("No videos met this criteria.")
			if(resolution == 'highest'):
				video = video_list[-1]
			else:
				video = video_list[0]
		else:
			result = []
			for v in yt.get_videos():
				if extension and v.extension != extension:
					continue
				elif resolution and v.resolution != resolution:
					continue
				else:
					result.append(v)
			matches = len(result)
			if matches <= 0:
				raise DoesNotExist("No videos met this criteria.")
			elif matches == 1:
				video = result[0]
			else:
				raise MultipleObjectsReturned("Multiple videos met this criteria.")
		video.download(path)

def batch_download_by_id_list(id_list, extension='mp4', resolution='highest', path='.'):
	'''Download videos by url list

	:param [str] id_list:
		A list of id of the YouTube videos
	:param str extension:
		The desired file extention. (e.g. mp4, flv)
		Take mp4 as the default value
	:param str resolution:
		The desired video broadcasting standard. (e.g. 720p, 1080p, highest, lowest)
		By choosing highest/lowest, the program would choose videio with the highest/lowest resolusion
		Take the highest resolution as the default choice
	:param str path:
		The destination output directory
	'''
	url_list = []
	for id in id_list:
		url_list.append("http://www.youtube.com/watch?v=" + id)
	batch_download_by_url_list(url_list, extension, resolution)
