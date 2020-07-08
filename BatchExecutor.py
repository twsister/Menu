import os
import subprocess
import re

root = 'dfl'

ENV = [
    ("%WORKSPACE%", "workspace"),
    ("%PYTHON_EXECUTABLE%", "python3"),
    ("%DFL_ROOT%", "dfl/_internal/DeepFaceLab")
]

error_code = 0


def process(contents):
    for t in ENV:
        contents = contents.replace(t[0], t[1]).replace("\\", "/")

    sections = re.split(r'\n\s*\n', contents)

    for section in sections:
        if "^" in section:
            tr = ""
            for part in section.replace("^", "").split("\n"):
                tr += " " + part.strip()
            _translate(tr.strip())
            continue
        if "(\n" in section:
            _translate(section.strip())
            continue
        lines = section.split('\n')
        for line in lines:
            _translate(line.strip())


def _at_echo(line):
    pass


def _echo(line):
    print(line[5:])


def _pause(line):
    input("Press Enter to continue...")


def _call(line):
    if "_internal/setenv.bat" in line:
        return
    print("This command (call) is not supported.")


def _mkdir(line):
    os.system("mkdir -p " + line.split(" ")[1])


def _rmdir(line):
    os.system("rm -rf " + line.split(" ")[1])


def _python(line):
    global error_code
    command = ["python3"]
    command.extend(line.replace('"', "").split(" ")[1:])
    error_code = subprocess.run(command).returncode


def _start(line):
    if "xnviewmp.exe" in line:
        os.system("gthumb " + line.split(" ")[-1])
        return
    print("This command ('start') is not supported")


def _cd(line):
    print("This command ('CD') is not supported")


def _if(line):
    def _neq(a, b):
        return a != b

    def _eq(a, b):
        return a == b

    ops = {
        'NEQ': _neq,
        'EQ': _eq
    }

    line = line.replace(")", "").replace("if ", "").replace("%errorlevel%", str(error_code)).split("(")
    condition = line[0].strip().split(" ")
    if ops[condition[1].strip()](condition[0].strip(), condition[2].strip()):
        _translate(line[1].strip())


buffer = ""

funcs = {
    "@echo": _at_echo,
    "echo": _echo,
    "pause": _pause,
    "call": _call,
    "mkdir": _mkdir,
    "rmdir": _rmdir,
    '"python3"': _python,
    "start": _start,
    "CD": _cd,
    "if": _if
}


def _translate(line):
    global buffer
    words = line.split(" ")
    if words[0] not in funcs:
        print(words[0], "is not a valid command")
        print(line)
        exit(1)

    funcs[words[0]](line)
