import time
import math

class Animator:
    def __init__(self, master, fps=60):
        self.master = master
        self.animations = [] 
        self.interval = int(1000 / fps)
        self._animate()

    def _animate(self):
        if self.animations:
            current_time = time.time()
            active = []
            for anim in self.animations:
                if anim.update(current_time):
                    active.append(anim)
            self.animations = active
        self.master.after(self.interval, self._animate)

    def animate(self, widget, prop, start, end, duration=0.3, easing='ease_out'):
        # Cancel existing anims for this prop
        self.animations = [a for a in self.animations if not (a.widget == widget and a.prop == prop)]
        
        if prop in ['fg_color', 'text_color', 'border_color', 'hover_color']:
            self.animations.append(ColorAnimation(widget, prop, start, end, duration))
        else:
            self.animations.append(Animation(widget, prop, start, end, duration, easing))

class Animation:
    def __init__(self, widget, prop, start, end, duration, easing='ease_out'):
        self.widget = widget
        self.prop = prop
        self.start = start
        self.end = end
        self.start_time = time.time()
        self.duration = duration
        self.easing = easing

    def update(self, now):
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            self._set(self.end)
            return False
            
        t = elapsed / self.duration
        
        if self.easing == 'ease_out':
            t = 1 - pow(1 - t, 3)
        elif self.easing == 'elastic':
            c4 = (2 * math.pi) / 3
            t = 0 if t == 0 else (1 if t == 1 else pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1)

        val = self.start + (self.end - self.start) * t
        self._set(val)
        return True

    def _set(self, val):
        try:
            if self.prop == 'x': self.widget.place(x=val)
            elif self.prop == 'y': self.widget.place(y=val)
            elif self.prop == 'w': self.widget.configure(width=val)
            elif self.prop == 'h': self.widget.configure(height=val)
            elif self.prop == 'val': self.widget.set(val)
            elif self.prop == 'relx': self.widget.place(relx=val)
            elif self.prop == 'rely': self.widget.place(rely=val)
        except: pass

class ColorAnimation(Animation):
    def __init__(self, widget, prop, start, end, duration):
        super().__init__(widget, prop, start, end, duration)
        self.start_rgb = self._to_rgb(start)
        self.end_rgb = self._to_rgb(end)

    def _to_rgb(self, color):
        # Handle CustomTkinter double-color list/tuple (Light, Dark)
        if isinstance(color, (list, tuple)):
            color = color[-1] # Pick the last one (Dark mode usually, or active mode)

        if not isinstance(color, str):
            return (0, 0, 0)

        # Handle standard names
        COLORS = {
            'white': '#FFFFFF',
            'black': '#000000',
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'transparent': '#000000' # Fallback
        }
        
        if color.lower() in COLORS:
            color = COLORS[color.lower()]
            
        # Handle hex
        if color.startswith('#'):
            color = color.lstrip('#')
            if len(color) == 3: color = ''.join([c*2 for c in color])
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
        # Fallback if unknown color name (e.g. return black)
        return (0, 0, 0)

    def _rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def update(self, now):
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            self._set(self.end)
            return False
            
        t = elapsed / self.duration
        # Linear for color usually looks best
        
        curr_rgb = (
            self.start_rgb[0] + (self.end_rgb[0] - self.start_rgb[0]) * t,
            self.start_rgb[1] + (self.end_rgb[1] - self.start_rgb[1]) * t,
            self.start_rgb[2] + (self.end_rgb[2] - self.start_rgb[2]) * t
        )
        self._set(self._rgb_to_hex(curr_rgb))
        return True

    def _set(self, val):
        try:
            if self.prop == 'fg_color': self.widget.configure(fg_color=val)
            elif self.prop == 'text_color': self.widget.configure(text_color=val)
            elif self.prop == 'border_color': self.widget.configure(border_color=val)
            elif self.prop == 'hover_color': self.widget.configure(hover_color=val)
        except: pass
