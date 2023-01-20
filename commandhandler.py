import threading
import sys


class CommandHandler:
    _VERSION_ = "1.0"

    def __init__(self, args):
        # Setup vars
        self.cmd_list = {"help": "List information about each command.",
                         "exit": "Exit the program."}
        self.exit_flag = False

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
        cmd = cmd.lower().split()
        if cmd[0] not in self.cmd_list.keys():
            print("Invalid Command!")
            return

        if cmd[0] == "exit":
            self.exit_handler()
        elif cmd[0] == "help":
            self.help_handler()

        elif cmd[0] == "setgain":
            self.setgain_handler(cmd)

    def help_handler(self):
        for command in self.cmd_list.keys():
            print("{} \t {}".format(command, self.cmd_list[command]))

    def exit_handler(self):
        self.exit_flag = True

    def setgain_handler(self, cmd):
        self.sdr.set_gain(cmd[1])
