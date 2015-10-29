#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from pytube import YouTube
import os
from .exceptions import MultipleObjectsReturned, PytubeError, CipherError, \
    DoesNotExist, AgeRestricted

class Batch(object):
	'''Class representation of a batch operation'''
	def __init__(self, extension='mp4', resolution='highest', path='.'):
		'''Initiating batch download wrapper.

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
		self.extension = extension
		self.resolution = resolution
		self.path = path

	def download_by_url_list(self, url_list):
		'''Download videos by url list

		:param [str] url_list:
			A list of url linked to the videos
		'''
		for url in url_list:
			try:
				video = self.fetch_video_by_url(url)
				video.download(self.path)
			except KeyboardInterrupt:
				path = os.path.normpath(self.path)
				os.remove(path)
				break
			except Exception as e:
				print("Failed to download {0}. {1}".format(url, e))
				continue

	def download_by_id_list(self, id_list):
		'''Download videos by id list

		:param [str] id_list:
			A list of id of the YouTube videos
		'''
		url_list = self.transfer_id_list_to_url_list(id_list)
		self.download_by_url_list(url_list)

	def merge_video_by_url_list(self, url_list):
		'''Download videos by url list and merge them into the same file

		:param [str] url_list:
			A list of url linked to the videos
		'''
		path = self.path
		if(os.path.isdir(os.path.normpath(path))):
			 path += "\\merged_video"
		for url in url_list:
			try:
				video = self.fetch_video_by_url(url)
				video.put_to_file(path)
			except KeyboardInterrupt:
				path = os.path.normpath(path)
				os.remove(path)
				break
			except Exception as e:
				print("Failed to download {0}. {1}".format(url, e))
				continue

	def merge_video_by_id_list(self, id_list):
		'''Download videos by id list and merge them into the same file

		:param [str] id_list:
			A list of id of the YouTube videos
		'''
		url_list = self.transfer_id_list_to_url_list(id_list)
		self.merge_video_by_url_list(url_list)

	def fetch_video_by_url(self, url):
		'''Fetch video by url

		:param [str] url:
			The url linked to a YouTube video
		'''
		yt = YouTube(url)
		if(self.resolution == 'highest' or self.resolution == 'lowest'):
			video_list = yt.filter(self.extension)
			if(len(video_list) == 0):
				raise DoesNotExist("No videos met this criteria.")
			if(self.resolution == 'highest'):
				video = video_list[-1]
			else:
				video = video_list[0]
		else:
			result = []
			for v in yt.get_videos():
				if self.extension and v.extension != self.extension:
					continue
				elif self.resolution and v.resolution != self.resolution:
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
		return video

	def transfer_id_list_to_url_list(self, id_list):
		'''
		Transfer a list of YouTube video id to links to YouTube videos

		:param [str] id_list:
			A list of id of the YouTube videos
		'''
		url_list = []
		for id in id_list:
			url_list.append("http://www.youtube.com/watch?v=" + id)
		return url_list
