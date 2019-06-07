#!/usr/bin/env python
# GIMP Plug-In.
# Only works on layer with alpha (RGBA).

import struct

from gimpfu import *

# Some parts based on https://stackoverflow.com/a/53383196 .

def pixels(layer):
	w,h=layer.width,layer.height
	region=layer.get_pixel_rgn(0,0,w,h)
	pix_chars=region[:,:]
	bpp=region.bpp
	colors=[]
	unpack_format='B'*bpp
	for i in range(0,len(pix_chars),bpp):
		color=struct.unpack(unpack_format,pix_chars[i:i+bpp])
		colors.append(color)
	return colors

def create_result_layer(image,name,colors):
	rlBytes=''
	bpp=len(colors[0])
	for i,c in enumerate(colors):
		if bpp==4:
			rlBytes+=struct.pack('BBBB',c[0],c[1],c[2],c[3])
		else:
			rlBytes+=struct.pack('BBB',c[0],c[1],c[2])

	rl=gimp.Layer(image,name,image.active_layer.width,image.active_layer.height,image.active_layer.type,100,NORMAL_MODE)
	region=rl.get_pixel_rgn(0,0,rl.width,rl.height,True)
	region[:,:]=rlBytes
	image.add_layer(rl,0)
	gimp.displays_flush()

def do_stuff(image):

	layer=pdb.gimp_image_get_active_layer(image)

	gimp.progress_init("Doing stuff to "+layer.name+"...")

	# Set up an undo group, so the operation will be undone in one step.
	pdb.gimp_undo_push_group_start(image)

	# Do stuff here.

	w,h=layer.width,layer.height
	colors=pixels(layer)
	colors_out=[None]*w*h

	for y in range(h):
		for x in range(w):
			i=x+y*w
			c=colors[i]
			# Only write empty pixels.
			if colors_out[i]==None:
				colors_out[i]=c
			# Don't expand empty pixels.
			if c[-1]==0:
				continue
			# Cardinal directions.
			indices=(i,i-w,i+w,i-1,i+1)
			for j in indices:
				if j>0 and j<len(colors_out):
					if colors[j][-1]==0:
						colors_out[j]=c

	create_result_layer(image,"Result",colors_out)

	# Close the undo group.
	pdb.gimp_undo_push_group_end(image)

register(
	"python_fu_pixinflate",
	"Pixel Inflate",
	"Inflate border pixels in four direction into empty area.",
	"crapola",
	"crapola",
	"2019",
	"Pixel Inflate",
	"RGBA",
	[
		(PF_IMAGE, "image", "Image", None),
	],
	[],
	do_stuff,menu="<Image>/Filters")

main()