import threading, _thread
import sys


class CommandHandler:
    _VERSION_ = "1.0"

    def __init__(self, args):
        # Setup vars
        self.cmd_list = {"help": "List information about each command.",
                         "exit": "Exit the program."}
        self.exit_flag = False

        if args.rtlsdr:
            self.cmd_list += {"setgain", "Set the gain of your RTLSDR",
                              "set"}

        print("Command Handler v{} initilized!".format(self._VERSION_))

        self.cmdthrd = threading.Thread(target=self.await_cmd)
        self.cmdthrd.daemon = True
        self.cmdthrd.start()
        self.cmdthrd.join()
        sys.exit()

    def await_cmd(self):
        while True:
            cmd = input("> ")
            self.handle_cmd(cmd)
            if self.exit_flag:
                break

    def handle_cmd(self, cmd):
        if cmd.lower() not in self.cmd_list.keys():
            print("Invalid Command!")

        if cmd == "exit":
            self.exit_flag = True
