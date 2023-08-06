from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.window import Window
from kivy import platform
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.lang.builder import Builder
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
import random
import time
from itertools import islice

from audio_handling import get_song_data

class MainWidget(RelativeLayout):
    NUM_LINES = 5
    LINE_SPACING = 0.15 # percentage in screen width
    BTN_HEIGHT = 0.05
    BTN_OFFSET_Y = 0.03
    BTN_TRANSPARENCY = 0.25
    NUM_TILES = 30
    SPEED = 0.005
    PRESS_THRESHOLD = 0.05
    
    lines = []
    
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    button1 = None
    button2 = None
    button3 = None
    button4 = None
    
    b1color = None
    b2color = None
    b3color = None
    b4color = None
    
    tile_colors = []
    tile_coordinates = []
    
    keybinds = {"b1":"a", "b2":"s", "b3":"k", "b4":"l"}
    pressed_keys = set()
    
    background = None
    
    button_coords = [[(0, 0) for _ in range(4)] for _ in range(4)]
    
    tiles = []
    

    song_data = None
    time_elapsed = 0
    time_start = 0
    
    song_path = 'audio/field.wav'
    song = None
    difficulty = "medium"
    
    score = {"miss": 0, "okay": 0, "good": 0, "great": 0, "perfect": 0}
    
    combo = 0
    multiplier = 1
    
    stat_txt = StringProperty("COMBO: 0\nACCURACY: 100.0%\nPERFECT: 0")
    
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_background()
        self.init_buttons()
        self.init_tiles()
        self.init_lines()
        self.init_audio()
        
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        self.keyboard.bind(on_key_up=self.on_keyboard_up)
        
        self.song_data = get_song_data(self.song_path, self.difficulty)
        
        Clock.schedule_interval(self.update, 1/60)
        
        Clock.schedule_interval(self.update_clock, 0.001)
        
        self.time_start = time.time()
        Clock.schedule_interval(self.place_tiles, 0.001)
        self.song.play()
    
    def init_audio(self):
        self.song = SoundLoader.load(self.song_path)
        
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard.unbind(on_key_up=self.on_keyboard_up)
        self.keyboard = None
        
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        for button, key in self.keybinds.items():
            if keycode[1] == key:
                self.button_pressed(button)
                if key not in self.pressed_keys:
                    self.tile_pressed(int(button[1]))
                self.pressed_keys.add(key)
                break
                
    def on_keyboard_up(self, keyboard, keycode):
        for button, key in self.keybinds.items():
            if keycode[1] == key and key in self.pressed_keys:
                self.button_released(button)
                self.pressed_keys.remove(key)
                break
    
    def button_pressed(self, button):
        match button:
            case "b1":
                self.b1color.rgba = (0, 1, 0, 1)
            case "b2":
                self.b2color.rgba = (1, 0, 0, 1)
            case "b3":
                self.b3color.rgba = (0, 0, 1, 1)
            case "b4":
                self.b4color.rgba = (1, 1, 0, 1)
    
    def button_released(self, button):
        match button:
            case "b1":
                self.b1color.rgba = (0, 1, 0, self.BTN_TRANSPARENCY)
            case "b2":
                self.b2color.rgba = (1, 0, 0, self.BTN_TRANSPARENCY)
            case "b3":
                self.b3color.rgba = (0, 0, 1, self.BTN_TRANSPARENCY)
            case "b4":
                self.b4color.rgba = (1, 1, 0, self.BTN_TRANSPARENCY)
    
    def tile_pressed(self, line):
        line_x = 0
        match line:
            case 1:
                line_x = self.get_line_x_by_index(-2)
            case 2:
                line_x = self.get_line_x_by_index(-1)
            case 3:
                line_x = self.get_line_x_by_index(0)
            case 4:
                line_x = self.get_line_x_by_index(1)
        
        for i, tile in enumerate(self.tile_coordinates):
            btn_height = self.height * self.BTN_HEIGHT
            thres_height = self.height * self.PRESS_THRESHOLD
            diff_y = abs(tile[1] - self.button_coords[line - 1][0][1]) # y coordinate of tile subtracted from LH corner of button
            
            if diff_y > btn_height + thres_height:
                continue
            elif tile[0] == line_x:
                # Add to current score based on accuracy of button press
                if diff_y <= btn_height * 0.05:
                    self.score["perfect"] += 1
                    self.combo += 1
                elif diff_y <= btn_height * 0.2:
                    self.score["great"] += 1
                    self.combo += 1
                elif diff_y <= btn_height * 0.4:
                    self.score["good"] += 1
                    self.combo += 1
                elif diff_y <= btn_height * 0.9:
                    self.score["okay"] += 1
                    self.combo += 1
                else:
                    self.score["miss"] += 1
                    self.combo = 0
                
                del self.tile_coordinates[i]
                break

    def init_tiles(self):
        for i in range(self.NUM_TILES):
            with self.canvas:
                self.tile_colors.append(Color(1, 1, 1))
                self.tiles.append(Quad())
                
    def place_tiles(self, dt):
        l1 = self.get_line_x_by_index(-2)
        l2 = self.get_line_x_by_index(-1)
        l3 = self.get_line_x_by_index(0)
        l4 = self.get_line_x_by_index(1)
        pitchMax = max(self.song_data.values())
        pitchMin = min(self.song_data.values())
        times = list(self.song_data.keys())
        
        
        top = self.height * 1.1
        # tile_height = self.height * self.BTN_HEIGHT
        for i, (btime, pitch) in enumerate(self.song_data.items()):
            if (btime - 0.08) <= self.time_elapsed <= (btime + 0.08) and self.NUM_TILES > len(self.tile_coordinates):
                rng = [1, 2, 3, 4]
                rep = 1
                if i < len(self.song_data) - 2:
                    if abs(times[i + 1] - times[i]) <= 0.15 and abs(times[i + 2] - times[i + 1]) <= 0.15:
                        rep += 2
                    elif abs(times[i + 1] - times[i]) <= 0.15:
                        rep += 1
                
                ### NOTE: GET AVERAGE OF PITCH INSTEAD OF MIN AND MAX
                if pitchMin <= pitch < int(pitchMax * 0.25):
                    self.tile_coordinates.append((l1, top))
                    rng.remove(1)
                elif int(pitchMin * 0.25) <= pitch < int(pitchMax * 0.5):
                    self.tile_coordinates.append((l2, top))
                    rng.remove(2)
                elif int(pitchMin * 0.5) <= pitch < int(pitchMin * 0.75):
                    self.tile_coordinates.append((l3, top))
                    rng.remove(3)
                elif int(pitchMin * 0.75) <= pitch <= pitchMax:
                    self.tile_coordinates.append((l4, top))    
                    rng.remove(4)    
                
                print(f'beat time: {btime} actual time: {self.time_elapsed} pitch: {pitch} reps: {rep}')
                
                for k in range(rep - 1):
                    r = random.choice(rng)
                    
                    match r:
                        case 1:
                            self.tile_coordinates.append((l1, top))
                        case 2:
                            self.tile_coordinates.append((l2, top))
                        case 3:
                            self.tile_coordinates.append((l3, top))
                        case 4:
                            self.tile_coordinates.append((l4, top))
                    
                    rng.remove(r)
                    
                for j in range(rep):
                    del self.song_data[next(islice(self.song_data, i + j, None))]
                break
    
    def update_tiles(self):
        if len(self.tile_coordinates) > 0:
            for i in range(len(self.tile_coordinates)-1, -1, -1):
                if self.tile_coordinates[i][1] < self.height * self.BTN_HEIGHT * -1:
                    del self.tile_coordinates[i]
                    self.score['miss'] += 1
                    self.combo = 0
                    
        if len(self.tile_coordinates) > 0:
            l1 = self.get_line_x_by_index(-2)
            l2 = self.get_line_x_by_index(-1)
            l3 = self.get_line_x_by_index(0)
            l4 = self.get_line_x_by_index(1)
            
            for i in range(len(self.tile_coordinates)):
                movement = self.SPEED * self.height
                self.tile_coordinates[i] = (self.tile_coordinates[i][0], self.tile_coordinates[i][1] - movement)
                
                tile = self.tiles[i]
                coords = self.tile_coordinates[i]

                tile_width = self.width * self.LINE_SPACING
                tile_height = self.height * self.BTN_HEIGHT
                
                xmin = coords[0]
                xmax = coords[0] + tile_width
                ymin = coords[1]
                ymax = coords[1] + tile_height
                
                x1, y1 = self.transform(xmin, ymin)
                x2, y2 = self.transform(xmin, ymax)
                x3, y3 = self.transform(xmax, ymax)
                x4, y4 = self.transform(xmax, ymin)
                
                tile.points = (x1, y1, x2, y2, x3, y3, x4, y4)
                
                x = self.tile_coordinates[i][0]
                if x == l1:
                    self.tile_colors[i].rgba = (0, 0.9, 0, 1)
                elif x == l2:
                    self.tile_colors[i].rgba = (0.9, 0, 0, 1)
                elif x == l3:
                    self.tile_colors[i].rgba = (0, 0, 0.9, 1)
                elif x == l4:
                    self.tile_colors[i].rgba = (0.9, 0.9, 0, 1)
        
        
        
    def init_background(self):
        with self.canvas:
            Color(0.1, 0.1, 0.1)
            self.background = Triangle()
    
    def update_background(self):
        lb_x = self.get_line_x_by_index(-2)
        rb_x = self.get_line_x_by_index(2)
        mid_x = self.perspective_point_x
        
        x1, y1 = self.transform(lb_x, 0)
        x2, y2 = self.transform(mid_x, self.perspective_point_y)
        x3, y3 = self.transform(rb_x, 0)
        
        self.background.points = (x1, y1, x2, y2, x3, y3)
        
    def init_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NUM_LINES):
                self.lines.append(Line(width=dp(2)))
                
    def get_line_x_by_index(self, index):
        spacing = self.width * self.LINE_SPACING
        return self.perspective_point_x + spacing * index
            
    def update_lines(self):
        offset = - int(self.NUM_LINES / 2)
        for i in range(self.NUM_LINES):
            line_x = self.get_line_x_by_index(offset)
            
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.perspective_point_y)

            self.lines[i].points = (x1, y1, x2, y2)
            offset += 1
            
    def transform(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y
        
        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = (diff_y / self.perspective_point_y) ** 3
        
        tr_x = self.perspective_point_x + diff_x * factor_y
        tr_y = self.perspective_point_y - factor_y*self.perspective_point_y
        
        return int(tr_x), int(tr_y)
    
    def init_buttons(self):
        with self.canvas:
            self.b1color = Color(0, 1, 0, self.BTN_TRANSPARENCY)
            self.button1 = Quad()
            self.b2color = Color(1, 0, 0, self.BTN_TRANSPARENCY)
            self.button2 = Quad()
            self.b3color = Color(0, 0, 1, self.BTN_TRANSPARENCY)
            self.button3 = Quad()
            self.b4color = Color(1, 1, 0, self.BTN_TRANSPARENCY)
            self.button4 = Quad()
            
    def update_buttons(self):
        currIndex = -2
        height = self.height * self.BTN_HEIGHT
        padding = self.BTN_OFFSET_Y * self.height
        
        #
        # 2      3
        #
        # 1      4
        
        # 0 = green, 1 = red, 2 = blue, 3 = yellow
        for i in range(len(self.button_coords)):
            left_x = self.get_line_x_by_index(currIndex)
            right_x = self.get_line_x_by_index(currIndex + 1)
            
            self.button_coords[i][0] = (left_x, padding)
            self.button_coords[i][1] = (left_x, padding + height)
            self.button_coords[i][2] = (right_x, padding + height)
            self.button_coords[i][3] = (right_x, padding)
            
            x1, y1 =  self.transform(*self.button_coords[i][0])
            x2, y2 =  self.transform(*self.button_coords[i][1])
            x3, y3 =  self.transform(*self.button_coords[i][2])
            x4, y4 =  self.transform(*self.button_coords[i][3])
            
            points = (x1, y1, x2, y2, x3, y3, x4, y4)
            
            match i:
                case 0:
                    self.button1.points = points
                case 1:
                    self.button2.points = points
                case 2:
                    self.button3.points = points
                case 3:
                    self.button4.points = points
            
            currIndex += 1
    
    def update_stat_txt(self):
        total = sum(self.score.values())
        weighted = self.score['perfect'] + self.score['great'] * 0.8 + self.score['good'] * 0.6 + self.score['okay'] * 0.4
        accuracy = (weighted / total) * 100 if total > 0 else 100
        self.stat_txt = f"COMBO: {self.combo}\nACCURACY: {'{:.1f}'.format(accuracy)}\nPERFECT: {self.score['perfect']}"
            
    def update_clock(self, dt):
        self.time_elapsed = time.time() - self.time_start
            
    def update(self, dt):
        time_factor = dt*60
        self.update_background()
        self.update_lines()
        self.update_buttons()
        self.update_tiles()
        self.update_stat_txt()

class BeatTrackApp(App):
    pass

BeatTrackApp().run()
    