import pygame
import events as e
import graphics as g
from visualmath import Graph
from loop import Loop
from time import time

def run(qubit, gf=10.0, pf=128.0):
    screen = pygame.display.set_mode(g.windowSize)
    screen.convert()
    pygame.display.set_caption('Qubit visualization')

    def graphics_update():
        screen.fill(g.CYAN)
        e.event_log.act(pygame.mouse.get_pos())
        qubit.draw(e.camera, g.WHITE, g.BLUE, g.RED, g.FOREST_GREEN, g.CYAN)
        g.draw(pygame.draw, screen)
        pygame.display.flip()
        gr.draw()

    physics = Loop(pf, time_dependent_func=qubit.step)

    gr = Graph((0, 1), (-1, 1))
    qubit.add_state_graph(gr, .2)

    stop = False
    last = time()

    graphics = Loop(gf, time_independent_func=graphics_update)
    graphics.init(last)

    physics.init(last)
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                e.event_log.log(event.key)
                if event.key == 32:
                    stop = True
            elif event.type == pygame.KEYUP:
                e.event_log.remove(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                e.event_log.click()
            elif event.type == pygame.MOUSEBUTTONUP:
                e.event_log.unclick()

        dt = time() - last
        graphics.go(dt)
        if not stop:
            physics.act(dt)

        last += dt

    pygame.display.quit()
