
import pygame, sys, time, random, json
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 1000, 600
surface=pygame.display.set_mode((WIDTH, HEIGHT),0,32)
fps=64
ft=pygame.time.Clock()
pygame.display.set_caption("Windows Management")



CONFIG = {}
with open("src/config.json", "r") as fobj:
    CONFIG = json.load(fobj)

title_font = pygame.font.SysFont("Arial", CONFIG["window"]["title_font"]["size"])

class Window:
    def __init__(self, title=""):
        self.title = title
        self.width = 500
        self.height = 300
        self.x = random.randint(0, WIDTH-self.width)
        self.y = random.randint(0, HEIGHT-self.height)
        # self.x = 100
        # self.y = 100
        self.last_data = [self.x, self.y, self.width, self.height]
        self.minimized = False
        self.is_fully_maximized = False
    def resize(self, x=0, y=0, width=500, height=300):
        self.last_data = [self.x, self.y, self.width, self.height]
        self.x, self.y, self.width, self.height = x, y, width, height
    def toggle_maximization(self):
        if self.is_fully_maximized:
            self.x, self.y, self.width, self.height = self.last_data
            self.is_fully_maximized = False
        else:
            full_height = HEIGHT-CONFIG["task_bar"]["height"]
            self.x, self.y = 0, 0
            self.width, self.height = WIDTH, full_height
            self.is_fully_maximized = True

class App:
    def __init__(self, name="", icon=None):
        self.name = name
        self.icon = icon
        self.windows = []
    def add_window(self):
        new_window = Window(self.name)
        self.windows.append(new_window)


class Home:
    def __init__(self, surface):
        self.surface = surface
        self.play = True
        self.mouse=pygame.mouse.get_pos()
        self.click=pygame.mouse.get_pressed()
        self.color = {
            "background": (255, 255, 255),
            "alpha": (0, 0, 0)
        }
        self.config = CONFIG
        windows_icon = pygame.image.load(self.config["task_bar"]["windows_icon"])
        self.windows_icon = pygame.transform.scale(windows_icon, (self.config["task_bar"]["icon_size"], self.config["task_bar"]["icon_size"]))
        wallpaper = pygame.image.load(self.config["wallpaper"])
        self.wallpaper = pygame.transform.scale(wallpaper, (WIDTH, HEIGHT-self.config["task_bar"]["height"]))
        self.apps = []
        self.load_apps()
        self.open_apps = []
        self.last_clicked = time.time()
        self.min_gap_between_clicks = 0.3
        self.holding_top_app = None
        self.last_clicked_for_dragging = time.time()
        self.min_gap_between_clicks_for_dragging = 0.25
    def load_apps(self):
        for app in self.config["apps"]:
            icon = pygame.image.load(app["icon"])
            icon = pygame.transform.scale(icon, (self.config["task_bar"]["icon_size"], self.config["task_bar"]["icon_size"]))
            new_app = App(app["name"], icon)
            self.apps.append(new_app)
    def draw_wallpaper(self):
        self.surface.blit(self.wallpaper, (0, 0))
    def draw_windows_icon(self):
        remaining_distance = self.config["task_bar"]["height"]-self.config["task_bar"]["icon_size"]
        top_y = HEIGHT-self.config["task_bar"]["height"]+(remaining_distance//2)
        self.surface.blit(self.windows_icon, (0, top_y))
    def check_clicks_for_task_bar(self, app_index_from_task_bar):
        if (time.time()-self.last_clicked)>=self.min_gap_between_clicks:
            if self.click[0]==1 or self.click[2]==1:
                if self.click[0]==1:
                    self.create_new_window_on_app(app_index_from_task_bar)
                elif self.click[2]==1:
                    self.minimize_or_maximize_all_windows(app_index_from_task_bar)
                self.last_clicked = time.time()
    def draw_app_in_task_bar(self, app, x, y):
        remaining_height = self.config["task_bar"]["height"]-self.config["task_bar"]["icon_size"]
        top_y = y+((remaining_height*3)/4)
        self.surface.blit(app.icon, (x, top_y))
        if (x)<=self.mouse[0]<=(x+self.config["task_bar"]["height"]) and (top_y)<=self.mouse[1]<=(top_y+self.config["task_bar"]["height"]):
            self.check_clicks_for_task_bar(self.apps.index(app))
        if len(self.open_apps)>0:
            # print (self.open_apps[0][0], self.apps.index(app))
            if self.open_apps[0][0]==self.apps.index(app):
                pygame.draw.rect(self.surface, self.color["alpha"], (x, top_y, self.config["task_bar"]["icon_size"], self.config["task_bar"]["icon_size"]), 1)
    def draw_window(self, window):
        if not window.minimized:
            x, y, width, height = window.x, window.y, window.width, window.height
            # whole window
            pygame.draw.rect(self.surface, self.config["window"]["background"], (x, y, width, height))
            # main bar
            pygame.draw.rect(self.surface, self.config["window"]["color"], (x, y, width, self.config["window"]["height"]))
            pygame.draw.rect(self.surface, self.color["alpha"], (x, y, width, self.config["window"]["height"]), 1)
            # close button
            close_x = x+width-(self.config["window"]["height"]*1)
            pygame.draw.rect(self.surface, self.config["window"]["close_color"], (close_x, y, self.config["window"]["height"], self.config["window"]["height"]))
            pygame.draw.rect(self.surface, self.color["alpha"], (close_x, y, self.config["window"]["height"], self.config["window"]["height"]), 1)
            # resize button
            resize_x = x+width-(self.config["window"]["height"]*2)
            pygame.draw.rect(self.surface, self.config["window"]["resize_color"], (resize_x, y, self.config["window"]["height"], self.config["window"]["height"]))
            pygame.draw.rect(self.surface, self.color["alpha"], (resize_x, y, self.config["window"]["height"], self.config["window"]["height"]), 1)
            # minimize button
            minimize_x = x+width-(self.config["window"]["height"]*3)
            pygame.draw.rect(self.surface, self.config["window"]["minimize_color"], (minimize_x, y, self.config["window"]["height"], self.config["window"]["height"]))
            pygame.draw.rect(self.surface, self.color["alpha"], (minimize_x, y, self.config["window"]["height"], self.config["window"]["height"]), 1)
            # title
            title_for_surface = title_font.render(window.title, False, self.config["window"]["title_font"]["color"])
            title_y = y+((self.config["window"]["height"]-self.config["window"]["title_font"]["size"])/2)
            title_x = x+10
            self.surface.blit(title_for_surface, (title_x, title_y))
            # whole window
            pygame.draw.rect(self.surface, self.color["alpha"], (x, y, width, height), 1)
    def draw_windows(self):
        for app_index in self.open_apps[::-1]:
            # print (app_index)
            self.draw_window(self.apps[app_index[0]].windows[app_index[1]])
        # print ()
    def draw_task_bar(self):
        x = self.config["task_bar"]["icon_size"]+self.config["task_bar"]["gap_between_apps"]
        y = HEIGHT-self.config["task_bar"]["height"]
        pygame.draw.rect(self.surface, self.config["task_bar"]["background"], (0, y, WIDTH, self.config["task_bar"]["height"]))
        for app in self.apps:
            self.draw_app_in_task_bar(app, x, y)
            x += self.config["task_bar"]["icon_size"]+self.config["task_bar"]["gap_between_apps"]
    def render(self):
        self.draw_wallpaper()
        self.draw_windows()
        self.draw_task_bar()
        self.draw_windows_icon()
    def any_window_clicked(self):
        for app_index in self.open_apps:
            window = self.apps[app_index[0]].windows[app_index[1]]
            if not window.minimized:
                x, y, width, height = window.x, window.y, window.width, window.height
                if (x)<=self.mouse[0]<=(x+width) and (y)<=self.mouse[1]<=(y+height):
                    return app_index
        return None
    def minimize(self, app_index):
        self.apps[app_index[0]].windows[app_index[1]].minimized = True
    def resize(self, app_index):
        self.apps[app_index[0]].windows[app_index[1]].toggle_maximization()
    def close(self, app_index):
        self.apps[app_index[0]].windows.pop(app_index[1])
        self.open_apps.remove(app_index[:])
    def make_front(self, app_index):
        self.open_apps.remove(app_index[:])
        self.open_apps.insert(0, app_index[:])
    def check_on_where_the_window_is_clicked(self, app_index):
        window = self.apps[app_index[0]].windows[app_index[1]]
        x, y, width, height = window.x, window.y, window.width, window.height
        close_x = x+width-(self.config["window"]["height"]*1)
        resize_x = x+width-(self.config["window"]["height"]*2)
        minimize_x = x+width-(self.config["window"]["height"]*3)
        if (y)<=self.mouse[1]<=(y+self.config["window"]["height"]):
            if (minimize_x)<=self.mouse[0]<(resize_x):
                self.minimize(app_index)
            elif (resize_x)<=self.mouse[0]<(close_x):
                self.resize(app_index)
            elif (close_x)<=self.mouse[0]<=(close_x+self.config["window"]["height"]):
                self.close(app_index)
            else:
                self.make_front(app_index)
        else:
            self.make_front(app_index)
    def minimize_or_maximize_all_windows(self, app_index_from_task_bar):
        for index in range(len(self.apps[app_index_from_task_bar].windows)):
            new_value = not self.apps[app_index_from_task_bar].windows[index].minimized
            self.apps[app_index_from_task_bar].windows[index].minimized = new_value
    def create_new_window_on_app(self, app_index_from_task_bar):
        self.apps[app_index_from_task_bar].add_window()
        latest_index = len(self.apps[app_index_from_task_bar].windows)-1
        self.open_apps.insert(0, [app_index_from_task_bar, latest_index])
    def any_app_clicked_from_task_bar(self):
        pass
    def check_clicks_for_windows(self):
        if self.click[0]==1:
            if (time.time()-self.last_clicked)>=self.min_gap_between_clicks:
                # print ("fuck")
                app_index = self.any_window_clicked()
                if app_index is not None:
                    self.check_on_where_the_window_is_clicked(app_index)
                self.last_clicked = time.time()
    def check_clicks(self):
        self.check_clicks_for_windows()
    def drag(self):
        # print (self.holding_top_app)
        if self.click[0]==1:
            if (time.time()-self.last_clicked_for_dragging)>=self.min_gap_between_clicks_for_dragging:
                if self.holding_top_app is None:
                    if len(self.open_apps)>0:
                        window = self.apps[self.open_apps[0][0]].windows[self.open_apps[0][1]]
                        if not window.minimized:
                            x, y, width, height = window.x, window.y, window.width, self.config["window"]["height"]
                            if (x)<=self.mouse[0]<=(x+width) and (y)<=self.mouse[1]<=(y+height):
                                self.holding_top_app = [self.mouse[0]-x, self.mouse[1]-y]
                else:
                    self.holding_top_app = None
                self.last_clicked_for_dragging = time.time()
        if self.holding_top_app is not None:
            if len(self.open_apps)>0:
                self.apps[self.open_apps[0][0]].windows[self.open_apps[0][1]].resize(self.mouse[0]-self.holding_top_app[0], self.mouse[1]-self.holding_top_app[1])
    def events(self):
        self.drag()
        self.check_clicks()
        # for app in self.apps:
        #     print (len(app.windows))
        # print ()
    def run(self):
        while self.play:
            self.surface.fill(self.color["background"])
            self.mouse=pygame.mouse.get_pos()
            self.click=pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==KEYDOWN:
                    if event.key==K_TAB:
                        self.play=False
            #--------------------------------------------------------------
            self.render()
            self.events()
            # print (self.open_apps)
            # -------------------------------------------------------------
            pygame.display.update()
            ft.tick(fps)



if  __name__ == "__main__":
    interface = Home(surface)
    interface.run()
