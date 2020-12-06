from pygame import display, init, draw, image, event
from os import system, remove, listdir
from sys import exit
from pygame.locals import QUIT
from Maria import network
from get_audio_output import *
from statistics import mean

class config:
	pix_size = 2
	lines, line_size = int(1800/pix_size), int(900/pix_size)

	neural_smooth = 2.5
	layers = [int(line_size/neural_smooth), line_size]

	background_color = (20, 20, 20)
	dark = 10

class video:
	duration = 10 # sec
	framerate = 25

	screen_coef = int(config.lines/(duration*framerate))

	def save_surface():
		filename = "./temp_output/"+str(int(window.line/video.screen_coef))+".png"
		image.save(window.screen, filename)

		audio.gen()

class audio:
	activate = True

	frq = (300, 1300)
	frame_time = int(video.duration/(video.framerate*video.duration)*100000)/100

	frames = []

	def gen():
		try:
			append_sinewave(freq=mean(audio.frames), duration_milliseconds=audio.frame_time, volume=1.0)
		except Exception as e:
			print(e)
			append_silence(audio.frame_time)

def positif(nbr):
	if(nbr < 0): return nbr*-1
	else: return nbr

def format_(nbr, min_=0, max_=0, positif=False, int_=False):
	if(positif and nbr < 0): nbr = nbr*-1
	if(nbr < min_+20): nbr = min_
	elif(nbr > max_-50): nbr = max_
	return nbr

class window:
	screen = None
	line = 0

	def event():
		for e in event.get():
			if(e.type == QUIT):
				print("\nEnd of process\n")
				exit()

	def new_line(data):
		window.event()
		colors = []
		if(audio.activate): audio.frames = []
		for i in range(config.line_size):
			color = int(format_((data[i]*config.dark)*255, 0, 200, True))
			color = positif(color-225)
			c = color


			div = 1
			for a in range(13):
				if(i+(a-6) >=0 and i+(a-6) < config.line_size): color += data[i+(a-6)]
			for b in range(5):
				if(i+(b-2) >=0 and i+(b-2) < config.line_size and network_.old_output): color += network_.old_output[i+(b-2)]

			color = (color+c/2)/6.2
			colors.append(color)

			if(color > 220): color = 255
			elif(color < 100 and color >30): color += -30

			color = format_(color, config.background_color[0], 255)

			draw.rect(window.screen, (color, color, color), (window.line*config.pix_size, i*config.pix_size, config.pix_size, config.pix_size))

			if(audio.activate): audio.frames.append(audio.frq[0] + color/255*(audio.frq[1]-audio.frq[0]))

		window.line+=1
		network_.old_output = colors
		draw.line(window.screen, (230, 10, 10), (window.line*config.pix_size, 0), (window.line*config.pix_size, config.line_size*config.pix_size), config.pix_size)
		display.update()

class network_:
	output = []
	old_output = False
	def learn():
		network.learn(10)
		network_.output = network.act([1])

def file_exist(file):
	try:
		with open(file): pass
		return True
	except IOError:
		return False

def EraseFile(repertoire):
	files = listdir(repertoire)
	for i in range(0,len(files)): remove(repertoire+'/'+files[i])

def create_output():
	nbr_output = 0
  
	while file_exist("./outputs/output"+str(nbr_output)+".mp4"): nbr_output += 1

	save_wav("./outputs/output_audio"+str(nbr_output)+".wav")
	system("ffmpeg -framerate "+str(video.framerate)+" -i ./temp_output/%01d.png \
	-i "+"./outputs/output_audio"+str(nbr_output)+".wav"+" ./outputs/output"+str(nbr_output)+".mp4")
	remove("./outputs/output_audio"+str(nbr_output)+".wav")
	EraseFile("./temp_output/")
	print("##### READY TO QUIT #####")

def init_all():
	init()
	window.screen = display.set_mode((int(config.lines*config.pix_size), int(config.line_size*config.pix_size)))
	window.screen.fill(config.background_color)

	network.config.tconnexion = 0.1
	network.init(1, config.layers, config.line_size)

init_all()

for i in range(config.lines):
	network_.learn()
	window.new_line(network_.output)

	if(i%video.screen_coef == 0):
		video.save_surface()

create_output()

while 1:
	window.event()
