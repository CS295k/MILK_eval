# CURD Recipe Parser

# Written by Frank Goodman (fgoodman)
# 9/9/14

from lxml import etree
from re import compile

def CURD_parse(filename):
  with open(filename, "r") as f:
    tree = etree.XML(f.read())

  unparsed_commands = [command.text for command in tree.findall(".//annotation")]

  PATTERN = compile(r"""((?:[^\,"']|"[^"]*"|'[^']*')+)""")

  commands = []
  for unparsed_command in unparsed_commands:
    command_name, unparsed_command = unparsed_command.split("(", 1)

    unparsed_command = unparsed_command.rstrip(")")

    arguments = PATTERN.split(unparsed_command)[1::2]

    arguments = [arg.replace("\"", "").strip() for arg in arguments]

    if arguments[0].startswith("{"):
      end = (i for i, v in enumerate(arguments) if v.endswith("}")).next()
      arguments = [{arg.lstrip("{").rstrip("}") for arg in arguments[0:end + 1]}] + arguments[end + 1:]

    arguments = [None if arg == "null" else arg for arg in arguments]

    commands.append((command_name, arguments))

  return commands
