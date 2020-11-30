from Nausicaa import network
from display import *
import pygame
from pygame.locals import *
import os
from get_audio_output import *
from statistics import mean

class config():
	lines = 900
	LenghtLine = 450
	FrameAct = 0
	couches = [100, 450]
	Adata = []

	IScolor = True
	color = (240, 240, 240)
	colorS = 60

	video_time = 10
	framerate_ = 25

	audio = True

	min_frq = 300
	max_frq = 1300

	audio_frame_time = int(video_time/(framerate_*video_time)*100000)/100
	print(audio_frame_time)
	scr_per_frame = int(lines/(video_time*framerate_))

	audio_frame = []

def init():
	screen.fill((20, 20, 20))
	network.config.tconnexion = 0.1
	network.init(1, config.couches, config.LenghtLine)
	part = network.act([1])
	network.learn(300, 1)

	data.sample_rate

def positif(nbr):
	if(nbr < 0): return nbr*-1
	else: return nbr

def file_exist(file):
	try:
		with open(file): pass
		return True
	except IOError:
		return False

def EraseFile(repertoire):
	files=os.listdir(repertoire)
	for i in range(0,len(files)):
		os.remove(repertoire+'/'+files[i])

def save_surf():
	filename = "./save/"+str(int(config.FrameAct/config.scr_per_frame))+".png"
	pygame.image.save(screen, filename)

def convert_surf():
	nbr_output = 0
  
	while file_exist("output"+str(nbr_output)+".mp4"):
		nbr_output += 1

	save_wav("output_audio"+str(nbr_output)+".wav")
	os.system("ffmpeg -framerate "+str(config.framerate_)+" -i ./save/%01d.png \
	-i "+"output_audio"+str(nbr_output)+".wav"+" output"+str(nbr_output)+".mp4")
	os.remove("output_audio"+str(nbr_output)+".wav")
	
	EraseFile("./save/")
def Event():
	for event in pygame.event.get():
		if(event.type==QUIT):
			print("\nEnd of process\n")
			sys.exit()

pygame.init()
screen = pygame.display.set_mode((config.lines*2, config.LenghtLine*2-10))

def Frame(data):
	config.audio_frame = []
	pygame.draw.line(screen, (250, 20, 20), (config.FrameAct*2+2, 0), (config.FrameAct*2+2, config.LenghtLine*2), 2)
	for i in range(config.couches[len(config.couches)-1]):
		try: dd = positif((data[i-4]+data[i-3]+data[i-2]+data[i-1]+data[i]+data[i+1]+data[i+2]+data[i+3]+data[i+4] + config.Adata[i-2]+config.Adata[i-1]+config.Adata[i]+config.Adata[i+1]+config.Adata[i+2])/14*255)
		except: dd = 255
		if(dd <config.colorS and config.IScolor): color = config.color
		elif(dd > 255): color = (20, 20, 20)
		else:
			dd = positif(dd-255)
			color = (dd, dd, dd)
			if(dd < 20): color = (20, 20, 20)
		if(config.audio):
			if(color == config.color): config.audio_frame.append(i/config.couches[len(config.couches)-1]*(config.max_frq-config.min_frq)+config.min_frq)
		pygame.draw.rect(screen, color, (config.FrameAct*2, i*2, 2, 2))
	
	if(config.FrameAct%config.scr_per_frame == 0): 
		save_surf()
		if(config.audio and config.FrameAct%(config.scr_per_frame) == 0):
			try:
				append_sinewave(freq=mean(config.audio_frame), duration_milliseconds=config.audio_frame_time, volume=1.0)
			except Exception as e:
				print(e)
				append_silence(config.audio_frame_time)
	
	config.FrameAct += 1
	config.Adata = data

init()

for i in range(config.lines):
	Event()
	network.learn(8, 1)
	Frame(network.act([1]))
	pygame.display.update()

convert_surf()
print("######## END")

while 1:
	Event()