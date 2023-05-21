from setup import *

class controller:
    def __init__(self,screen,outputq=None,inputq=None,event=None):
        self._output = outputq
        self._input = inputq
        self._screen = screen
        self._pause = False
        self._event = event

    def run(self):
        log("Controller run")
        while True:
            log("Controller loop")
            self._event.wait()
            char = self._screen.getch()

            # # check queue if not empty, or paused
            # if self._input.qsize() or self._pause:
            #     update = self._input.get()
            #     if update["type"] == "quit": return
            #     # if update["type"] == "pause": self._pause=update["value"]


            self._output.put(char)

            # # check to see if quitting
            # if chr(char)=="q":



