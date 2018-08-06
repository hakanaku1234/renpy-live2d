import renpy.exports as renpy
import ctypes
from ctypes import util, c_float
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from live2d.wrapper import PyCubismFramework, PyCubismUserModel, PyCubismModelSettingJson, PyLAppModel
import json
import os
import pygame
                      
class Live2DDisplayable(renpy.Displayable):
        
    def __init__(self, **kwargs):
        super(Live2DDisplayable, self).__init__(**kwargs)
    
        self.framebuffer = 0
        self.render_texture = 0
        self.render_buffer_depth = 0
                
        PyCubismFramework.startup()        
        PyCubismFramework.initialize()
        # TODO: Do not forget to call 'PyCubismFramework.dispose()'.
                                
    def texture_loader(self, path):        
        glActiveTexture(GL_TEXTURE0)
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        surface = pygame.image.load(path)
        BYTEP = ctypes.POINTER(ctypes.c_ubyte)
        surface_pixels_ptr = ctypes.cast(surface._pixels_address, BYTEP)
            
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface.get_width(), surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, surface_pixels_ptr)
 
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        return texture_id
            
    def render(self, width, height, st, at):            
        if self.framebuffer == 0:
            self.create_framebuffer()
            self.create_live2d_model()
                        
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)            
        
        glUseProgram(0)
        
        glViewport(0, 0, 1024, 1024)
        
        glClearColor(0, 0, 0, 1)             
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
            
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
                
        glFrontFace(GL_CCW)
            
        self.model.update()
        self.model.draw()
                                                
        result = renpy.Render(1024, 1024)                
        surface = result.canvas().get_surface()
        surface.lock()
        glPixelStorei(GL_PACK_ROW_LENGTH, surface.get_pitch() // surface.get_bytesize())
        glReadPixels(0, 0, 1024, 1024, GL_RGBA, GL_UNSIGNED_BYTE, surface._pixels_address)
        glPixelStorei(GL_PACK_ROW_LENGTH, 0)
        surface.unlock()
                                
        surface_rotated = pygame.transform.rotate(surface, 180)
        surface.blit(surface_rotated, (0, 0))
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
                        
        # result.fill("#FF0000")
        # TODO: Slow, allocates one surface every time.
        # surface = result.canvas().get_surface()
        # surface.lock() 
        # width * height * sizeof(GLubyte) * 3
        # TODO: https://github.com/bitsawer/renpy-shader/blob/7ce330370397a160fe1369823294d26b6be129ee/ShaderDemo/game/shader/controller.py#L163
        # pixels = ( GLubyte * (3*1024*1024) )(0)
        # glReadPixels(0, 0, 1024, 1024, GL_RGBA, GL_UNSIGNED_BYTE, surface._pixels_address)
        # surface.unlock()
                                        
        renpy.display.render.redraw(self, 0.06)
                
        return result
        
    def create_framebuffer(self):            
        # Create FBO texure.
    
        self.render_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.render_texture)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1024, 1024, 0, GL_RGBA, GL_UNSIGNED_BYTE, [])
            
        # Create FBO.
    
        self.framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        
        # Attach FBO textures.
    
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.render_texture, 0)
            
        # self.framebuffer = glGenFramebuffers(1)
        # glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        #
        # self.render_texture = glGenTextures(1)
        #
        # glBindTexture(GL_TEXTURE_2D, self.render_texture)
        # glTexImage2D(GL_TEXTURE_2D, 0,GL_RGBA, 1024, 1024, 0,GL_RGBA, GL_UNSIGNED_BYTE, [])
        #
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        #
        # self.render_buffer_depth = glGenRenderbuffers(1)
        #
        # glBindRenderbuffer(GL_RENDERBUFFER, self.render_buffer_depth)
        # glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, 1024, 1024)
        # glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.render_buffer_depth)
        #
        # glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, self.render_texture, 0)
        #
        # glDrawBuffers(1, [GL_COLOR_ATTACHMENT0])
        #
        # if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        #     print("Failed to create FBO.")
        # else:
        #     print("FBO created.")      
                    
    def create_live2d_model(self):
        self.model = PyLAppModel()
        self.model.set_texture_loader(self.texture_loader)
        # self.model.load_assets(u'/Users/asfdfdfd/Work/asfdfdfd/ProjectLive2D/game/live2d_resources/Haru/', u'Haru.model3.json')
        self.model.load_assets(u'/Users/asfdfdfd/Work/asfdfdfd/ProjectLive2D/game/live2d_resources/Hiyori/', u'Hiyori.model3.json')
        # self.model.load_assets(u'/Users/asfdfdfd/Work/asfdfdfd/ProjectLive2D/game/live2d_resources/Mark', u'Mark.model3.json')
        
        self.model.set_random_expression()
                
    def render_live2d(self):
        self.model.update()
                
        self.model.draw()
        