from setup import *

class controller:
    def __init__(self,screen,charq=None,outputq=None,inputq=None,event=None):
        self._output = outputq
        self._charq = charq
        self._input = inputq
        self._screen = screen
        self._pause = False
        # self._event = event

    #: def pause(self):
    #     """ Pause view output """
    #     self._output.put({"type":"confirm_pause"})
    #     while self._input.get()["type"]!="resume":
    #         log(f"=========================== CHARACTER: Pause loop")
    #         time.sleep(0.05)
    #     self._output.put({"type":"confirm_resume"})

    def run(self):
        log("CONTROLLER: run")
        while True:

#             if not self._input.empty():
#                 log(f"=========================== CHARACTER: Pausing!")
#                 update = self._input.get()
#                 if update["type"]=="pause": 
#                     self.pause()
#             else:

            char = self._screen.getch()
            # log(f"=========================== CHARACTER: {chr(char)}")
            self._charq.put(char)
