import pygame
import sys
import os


WIDTH = 1200
HEIGHT = 750

FPS = 50
clock = pygame.time.Clock()
pygame.init()

size = width, height = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)

List_Buttons = []

buttons = pygame.sprite.Group()
but_menu = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls = pygame.sprite.Group()
student_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
x_start, y_start = 0, 0
Start_screen = True
restart = False
Lvl = ""
tile_width = tile_height = 50


# Classes
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, function, image, image_point, function_arg=None):
        super().__init__()
        self.image_now = load_image(image)
        self.image_pointing = load_image(image_point)
        self.image = self.image_now
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.function = function
        self.function_arg = function_arg

    def update(self, *args):
        if args and self.rect.collidepoint(args[0].pos):
            if args[0].type == pygame.MOUSEBUTTONDOWN:
                return self.function(self.function_arg)
            else:
                self.image = self.image_pointing
        else:
            self.image = self.image_now


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            x_start + tile_width * pos_x, y_start + tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.frames = []
        self.cut_sheet(player_image, 4, 4)
        self.cur_frame = 0
        self.number_frame = 0
        self.image = self.frames[self.number_frame][self.cur_frame]
        self.rect = self.image.get_rect().move(
            x_start + tile_width * pos_x + (tile_width - self.image.get_rect().width) // 2,
            y_start + tile_height * pos_y + (tile_height - self.image.get_rect().height) // 2)
        self.dx = 0
        self.dy = 0

    def get_keys(self):
        keys = pygame.key.get_pressed()
        m_keys = pygame.mouse.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
           self.dx = -tile_width
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.dx = tile_width
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.dy = -tile_height
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.dy = tile_height

    def update(self):
        self.get_keys()
        self.rect.x += self.dx
        self.rect.y += self.dy
        true = True
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x -= self.dx
            self.rect.y -= self.dy
            true = False
        else:
            sprite = pygame.sprite.spritecollideany(self, student_group)
            if sprite:
                if not sprite.move(self.dx, self.dy):
                    self.rect.x -= self.dx
                    self.rect.y -= self.dy
                    true = False
        if true:
            if self.dx > 0:
                self.number_frame = 3
            elif self.dx < 0:
                self.number_frame = 2
            elif self.dy < 0:
                self.number_frame = 1
            else:
                self.number_frame = 0
        self.dx = 0
        self.dy = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            f = []
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                f.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
            self.frames.append(f)

    def anim(self):
        self.cur_frame = (self.cur_frame + 0.1) % len(self.frames[self.number_frame])
        self.image = self.frames[self.number_frame][int(self.cur_frame)]


class Student(pygame.sprite.Sprite):
    def __init__(self, image_st, pos_x, pos_y, type):
        super().__init__(student_group)
        self.frames = []
        self.cut_sheet(tile_images[image_st], 4, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.type = type
        self.rect = self.image.get_rect().move(
            x_start + tile_width * pos_x + (tile_width - self.image.get_rect().width) // 2,
            y_start + tile_height * pos_y + (tile_height - self.image.get_rect().height) // 2)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x -= dx
            self.rect.y -= dy
            return False
        for i in student_group:
            if i is self:
                continue
            if pygame.sprite.collide_mask(self, i):
                self.rect.x -= dx
                self.rect.y -= dy
                return False
        return True

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.anim()

    def anim(self):
        self.cur_frame = (self.cur_frame + 0.1) % len(self.frames)
        self.image = self.frames[int(self.cur_frame)]


class ClassExit(pygame.sprite.Sprite):
    def __init__(self, image_st, image_d, pos_x, pos_y, type):
        super().__init__(all_sprites)
        self.type = type
        self.image_deactive = tile_images[image_d]
        self.active = tile_images[image_st]
        self.image = self.image_deactive
        self.rect = self.image.get_rect().move(x_start + tile_width * pos_x,
                                               y_start + tile_height * pos_y)

    def update(self):
        sprite = pygame.sprite.spritecollideany(self, student_group)
        if sprite:
            if sprite.type == self.type:
                self.image = self.active
            else:
                self.image = self.image_deactive
        else:
            self.image = self.image_deactive


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def restart_level(none=None):
    global RUN, restart
    restart = True
    RUN = False


def terminate():
    pygame.quit()
    sys.exit()


def button_level(map):
    global Start_screen, Lvl
    Start_screen = False
    Lvl = map


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Нажмите любую клавишу для начала",
                  "Управление стрелками, пробел действие"]
    buttons.add(Button(50, 300, button_level, "button_test.jpg", "button_test_pointer.jpg", "level1.txt"))
    buttons.add(Button(50, 370, button_level, "button_test.jpg", "button_test_pointer.jpg", "level2.txt"))
    fon = pygame.transform.scale(load_image('start_screen_fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                buttons.update(event)
            if event.type == pygame.MOUSEMOTION:
                buttons.update(event)
        buttons.draw(screen)
        if not Start_screen:
            return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('#')
    return list(map(lambda x: x.ljust(max_width, '#'), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'exit_m': load_image('Exit_ordinary_active.png'),
    'exit_e': load_image('Exit_ordinary_active.png'),
    'exit_f': load_image('Exit_ordinary_active.png'),
    'pl_m': load_image('Person3.png'),
    'exit_m_d': load_image('Exit_ordinary.png'),
    'exit_e_d': load_image('Exit_ordinary.png'),
    'exit_f_d': load_image('Exit_ordinary.png'),
    "pl_f": load_image('Химик (2).png'),
    "pl_e": load_image('Person4.png'),
}
player_image = load_image('proger.png')


'''
. - пустая клетка
@ - стена
P - игрок
M - выход для инженер 
m - инженер
F - выход для химика
f - химик
E - выход для экономиста
e - экономист
'''
def generate_level(level):
    global x_start, y_start
    new_player, x, y = None, None, None
    x_start, y_start = (WIDTH - len(level[0]) * tile_width) // 2, (HEIGHT - len(level) * tile_height) // 2
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '@':
                #Tile('wall', x, y)
                walls.add(Tile('wall', x, y))
            elif level[y][x] == 'P':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'M':
                ClassExit('exit_m', 'exit_m_d', x, y, 0)
            elif level[y][x] == 'm':
                Tile('empty', x, y)
                Student('pl_m', x, y, 0)
            elif level[y][x] == 'F':
                ClassExit('exit_f', 'exit_f_d', x, y, 0)
            elif level[y][x] == 'f':
                Tile('empty', x, y)
                Student('pl_f', x, y, 0)
            elif level[y][x] == 'E':
                ClassExit('exit_e', 'exit_e_d', x, y, 0)
            elif level[y][x] == 'e':
                Tile('empty', x, y)
                Student('pl_e', x, y, 0)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def main(none=None):
    global RUN, restart, but_menu, all_sprites, tiles_group, walls, student_group, player_group, Start_screen
    if not restart:
        Start_screen = True
    start_screen()
    but_menu = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    student_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    restart = False
    player, level_x, level_y = generate_level(load_level(Lvl))
    RUN = True
    fon = pygame.transform.scale(load_image('start_screen_fon.jpg'), (WIDTH, HEIGHT))
    but_menu.add(Button(WIDTH - 100, 10, restart_level, "Restart.png", "Restart_point.png"))
    but_menu.add(Button(WIDTH - 180, 10, main, "Menu.png", "Menu_point.png"))
    screen.blit(fon, (0, 0))
    while RUN:  # главный игровой цикл
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            if event.type == pygame.KEYDOWN:
                player.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                but_menu.update(event)
            if event.type == pygame.MOUSEMOTION:
                but_menu.update(event)
        all_sprites.draw(screen)
        but_menu.draw(screen)
        student_group.draw(screen)
        player_group.draw(screen)
        player.anim()
        student_group.update()
        pygame.display.flip()  # смена кадра
        # изменение игрового мира
        all_sprites.update()
        clock.tick(FPS)
    if restart:
        main()
    pygame.quit()


if __name__ == '__main__':
    main()