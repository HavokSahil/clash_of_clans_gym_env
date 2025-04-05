class StateManager:
    def __init__(self, manager):
        self.manager = manager
        self.current_state = None

    def set_state(self, state):
        if self.current_state:
            self.current_state.clean_up()
        
        self.current_state = state
        self.current_state.on_enter()

    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)