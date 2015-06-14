"""
Project expectations:
A1.3 demonstrate the ability to use non-numeric comparisons (e.g., strings, comparable interface) in computer programs;
A1.5 describe and use one-dimensional arrays of compound data types (e.g., objects, structures, records) in a computer
     program.
A2.2 use modular design concepts that support reusable code (e.g., encapsulation, inheritance, method overloading,
     method overriding, polymorphism);
A3.1 demonstrate the ability to read from, and write to, an external file (e.g., text file, binary file, database, XML
     file) from within a computer program;
A3.3 create subprograms to insert and delete array elements;
A4.1 work independently, using support documentation (e.g., IDE Help, tutorials, websites, user manuals), to resolve
     syntax issues during software development;
A4.3 create fully documented program code according to industry standards (e.g., doc comments, docstrings, block
     comments, line comments);
A4.4 create clear and maintainable external user documentation (e.g., Help files, training materials, user manuals).

B1.7 demonstrate the ability to use shared resources to manage source code effectively and securely (e.g., organize
     software components using shared files and folders with timestamps, and proper version control).
B2.2 demonstrate the ability to meet project goals and deadlines by managing individual time during a group project;

C1.1 decompose a problem into modules, classes, or abstract data types (e.g., stack, queue, dictionary) using an
     object-oriented design methodology (e.g., CRC [Class Responsibility Collaborator] or UML [Unified Modeling
     Language]);
C1.4 apply the principle of re-usability in program design (e.g., in modules, subprograms, classes, methods, and
     inheritance).
"""
import tools
import sys
import pygame
from pygame.locals import *

# constants
resolution = (511, 511)
tile_size = (32, 32)

player = tools.Player()
level = tools.Level('level1', resolution, tile_size, player)

# initialize PyGame
pygame.init()
main_clock = pygame.time.Clock()
display_surface = pygame.display.set_mode(resolution)
pygame.display.set_caption('ICS4U Tile Based Game')
pygame.display.set_icon(pygame.image.load('resources/icon.png'))
pygame.mixer.music.load('resources/background.ogg')
pygame.mixer.music.play()

# initialize the HUD
hud = tools.HudOverlay()
hud.update_money(25)

display_surface.blit(level.background, (0, 0))  # draw background to screen

effect = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    if not effect:
        # handle keyboard input
        diagonal_check = False
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            if level.bounds.rect_membership((player.hitbox.x, player.hitbox.y - 1), (player.hitbox.w, player.hitbox.h), player):
                player.pos[1] -= 1
            diagonal_check = True
            player.update(1)

        elif keys[K_DOWN]:
            if level.bounds.rect_membership((player.hitbox.x, player.hitbox.y + 1), (player.hitbox.w, player.hitbox.h), player):
                player.pos[1] += 1
            diagonal_check = True
            player.update(3)

        if keys[K_LEFT]:
            if level.bounds.rect_membership((player.hitbox.x - 1, player.hitbox.y), (player.hitbox.w, player.hitbox.h), player):
                player.pos[0] -= 1
            if not diagonal_check:
                player.update(4)

        elif keys[K_RIGHT]:
            if level.bounds.rect_membership((player.hitbox.x + 1, player.hitbox.y), (player.hitbox.w, player.hitbox.h), player):
                player.pos[0] += 1
            if not diagonal_check:
                player.update(2)

        # check for collisions with doors
        collisions = level.entities.collisions()
        if collisions:
            for i in collisions:
                if i.flag in {'level1', 'level2'}:
                    effect = 32
                    level = tools.Level(i.flag, resolution, tile_size, player)
                    player.update(3, force_update=True)
                elif i.flag == 'coin':
                    level.entities.kill(i)
                    # TODO: Move this into Entity class eventually
                    coin_sound = pygame.mixer.Sound('resources/coin.wav')
                    coin_sound.set_volume(0.4)
                    coin_sound.play()
                    player.money += 5

    # back-to-front blitting of images
    display_surface.blit(level.background, (0, 0))

    # blit all items
    for i in level.entities.entity_list:
        if type(i) != tools.entity.Door:
            display_surface.blit(i.current_sprite, i.pos)
            i.update()

    display_surface.blit(player.current_sprite, (player.pos[0], player.pos[1]))  # y shifted down 8 px

    # effects
    if effect:
        display_surface.blit(tools.fade(resolution, effect), (0, 0))
        effect -= 1

    # HUD
    display_surface.blit(hud.overlay, (8, 463))
    display_surface.blit(hud.update_money(player.money), (88, 463))
    display_surface.blit(hud.update_health(player.health), (344, 463))

    pygame.display.update()
    main_clock.tick(60)
