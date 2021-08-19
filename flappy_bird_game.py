import pygame
import neat
import time
import os
import random
pygame.font.init()

# create the size of the window
WIN_WIDTH = 500 # constants are to written in the capital
WIN_HEIGHT = 800
GEN = 0

# load all the images(bird1, bird2, bird3) from the folder imgs 
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))] # scale2x gonna make the size of the image to be double of their previous size, 
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png"))) # the pipes image
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png"))) # base or the ground image
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png"))) # background image

STAT_FONT = pygame.font.SysFont("comicsans", 50) # font for the score
class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25 # max rotation means how much the bird is gonna tilt when moving upwards like we need to point the nose of the bird up when moving upwards and point downwards when moving downwards
	ROT_VEL = 20 # rotation velocity is how much we will rotate on each frame every time that we move the bird
	ANIMATION_TIME = 5 # how long we gonna show each bird animation or how fast or slow the birds are going to move their wings 

	def __init__(self, x, y):
		self.x = x # x and y are the starting pos of the bird
		self.y = y 
		self.tilt = 0 # for each bird we gonna have a tilt to know how much that bird has tilted so we know how to draw it on the screen
		self.tick_count = 0 
		self.vel = 0 # velocity of the bird
		self.height = self.y 
		self.img_count = 0 # this is for which bird image we are currently showing so we can animate it
		self.img = self.IMGS[0] # pos 0 is first image of the bird

	def jump(self): # to jump upwards
		self.vel = -10.5 # -ve bcz the top left corner of the window is (0,0) so when we move up the velocity is going to be -ve and when down the velocity is +ve
		self.tick_count = 0 # keep track when we last jumped
		self.height = self.y # keep track of where the bird jumped from or where it came from

	def move(self): # it is what we call every single frame to move our bird
		self.tick_count += 1 # frame went by and how many times we moved since the last jump
		d = self.vel * self.tick_count + 1.5*self.tick_count**2 # how many pixels we are moving up or down this frame, this is what we end up moving when we change the y pos of the bird, based on the current bird's velocity we are calc how much we are moving up or down

		if d >= 16: # if we are moving down more than 16 pixels than move only 16
			d = 16

		if d < 0: # means we are moving upwards
			d -= 2 # to fine-tuned the movement of the bird

		self.y += d # add it to the y to move slowly upwards or downwards
		# tilt the bird acc to where we are moving
		if d < 0 or self.y < self.height + 50: # d < 0 means we are moving upwards
			if self.tilt < self.MAX_ROTATION: # so that we are not tilting the birds completely backwards or crazy direction
				self.tilt = self.MAX_ROTATION # tilt the bird 25 degrees 

		else: # rotate the bird downwards
			if self.tilt > -90: # bcz when we are going downwards we don't want to tilt the bird 25 deg like going upwards we wanna tilt the bird completely downwards 90 degrees
				self.tilt -= self.ROT_VEL

	def draw(self, win): # draw the bird on the window
		self.img_count += 1 # how many ticks we have shown a current image for (tick means how many times the main while game loop run)
		# get the bird with wings flapping up and down
		if self.img_count < self.ANIMATION_TIME: # if the img_count < 5
			self.img = self.IMGS[0] # then show the first image
		elif self.img_count < self.ANIMATION_TIME*2: # < 10
			self.img = self.IMGS[1] # then show the second image
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4: # then again go back to the first image, we can't reset the wings of the bird here bcz it will look like we skipped a frame so reset the count in the second one
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		if self.tilt <= -80: # when the bird is moving down
			self.img = self.IMGS[1] # then we don't want the bird to flap its bird, it should look like it is falling down
			self.img_count = self.ANIMATION_TIME*2 # so it doesn't look like it skipped a frame

		rotated_image = pygame.transform.rotate(self.img, self.tilt) # rotates the img around the top left corner
		new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center) # rotate the img around the center
		win.blit(rotated_image, new_rect.topleft) # blit means draw on the window

	def get_mask(self): # when we have collision for the objects 
		return pygame.mask.from_surface(self.img) # it gives a 2d list in which it has values in where the pixels are present in the picture(the background will be transparent where the pixels are not present)

class Pipe:
	GAP = 200 # how much space is between the pipes
	VEL = 5 # how fast the pipes move bcz the bird will stay there but everything will be moving

	def __init__(self, x):
		self.x = x # only x not y bcz the height of the pipes or the y axis will be random everytime
		self.height = 0

		self.top = 0 # where the top and the bottom of the pipe is gonna be drawn
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # we have to flip the pipe to make it upside down
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False # if the bird has passed the current pipe or not
		self.set_height()

	def set_height(self): # define where the top and the bottom of the pipe is and how the long it is
		self.height = random.randrange(50, 450) # 50 - 450
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL # move the pipe to the left based on the velocity

	def draw(self, win): # draw the pipes
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird, win): # its gonna compare the masks of two images(bird and pipes) list by list and check if the pixels overlap that means there is collison 
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y)) # dis of the bird from the top pipe, round the value bcz we don't want the decimal values
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset) # get the overlap between the bird mask and the bottom pipe
		t_point = b_point = bird_mask.overlap(top_mask, top_offset) # they both gonna return None when if there is no collision

		if t_point or b_point: # if there is a collision then return True
			return True

		return False

class Base:
	VEL = 5 # keep the same velocity as the pipe 
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG 

	def __init__(self, y): # we don't need to define the x bcz its gonna move to the right pos
		self.y = y 
		self.x1 = 0 # we will have two base img when the first one is off the screen the second one will be right behind the other one and they both will be moving at the same time.  
		self.x2 = self.WIDTH # the second base is right after the first one so start at the width

	def move(self):
		self.x1 -= self.VEL  # move them with same velocities
		self.x2 -= self.VEL 

		if self.x1 + self.WIDTH < 0: # if one of them is off the screen then we cycle it back after the second one
			self.x1 = self.x2 + self.WIDTH 

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH 

	def draw(self, win): # draw the base
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen): # draw the bird, pipes, base
	win.blit(BG_IMG, (0,0)) # draw the bird on the top left corner

	for pipe in pipes: # pipes will be in list
		pipe.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

	text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
	win.blit(text, (10, 10))

	base.draw(win)
	for bird in birds:
		bird.draw(win)
	pygame.display.update() # update the dislay

def main(genomes, config):
	global GEN 
	GEN += 1
	nets = []
	ge = []
	birds = []

	for _, g in genomes:
	    net = neat.nn.FeedForwardNetwork.create(g, config) # setting up a neural network for the genome
	    nets.append(net)
	    birds.append(Bird(230,350))
	    ge.append(g)
	    g.fitness = 0  # start with fitness level of 0

	base = Base(730) # height is 730
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()

	score = 0

	run = True
	while run:
		clock.tick(30) # do 30 ticks every second
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1
		else:
			run = False 
			break 

		for x, bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 0.1 # encourage the bird to fly

			# send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

			if output[0] > 0.5: # jump the bird if the output is more than 0.5
				bird.jump()

		# bird.move()
		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird, win):
					ge[x].fitness -= 1 # everytime the bird hits a pipe then 1 is going to be removed from the fitness score
					birds.pop(x) # remove the bird
					nets.pop(x) # the neural network associated with it
					ge.pop(x) # remove the genome
				if not pipe.passed and pipe.x < bird.x: # checked if we have passed the pipe
					pipe.passed = True
					add_pipe = True # add another pipe 

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: # means the pipe has passed the screen
				rem.append(pipe)

			pipe.move()

		if add_pipe:
			score += 1
			for g in ge:
				g.fitness += 5 # increase the fitness of the bird to encourage to go further through the pipes 
			pipes.append(Pipe(600)) # add the pipes

		for r in rem:
			pipes.remove(r)

		for x, bird in enumerate(birds): # if the bird hits the ground then remove the birds, neural network, genome
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x) 
 
		base.move()
		draw_window(win, birds, pipes, base, score, GEN)



def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

	p = neat.Population(config) # generate the population based on the config file

	# Add a stdout reporter to show progress in the terminal.
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats) # the output that we are going to see

	winner = p.run(main, 50) # fitness func is main which will be used to evaluate to the population of the birds, this will run 50 times

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__) # give the path to the directory that we are currently in
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)