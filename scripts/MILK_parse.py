# MILK Recipe Parser

# Written by Frank Goodman (fgoodman)
# 9/9/14

from lxml import etree
from re import compile

PATTERN = compile(r"""((?:[^\,"']|"[^"]*"|'[^']*')+)""")

def MILK_parse_command(unparsed_command):
  command_name, unparsed_command = unparsed_command.split("(", 1)

  unparsed_command = unparsed_command.rstrip(")")

  arguments = PATTERN.split(unparsed_command)[1::2]

  arguments = [arg.replace("\"", "").strip() for arg in arguments]

  if arguments[0].startswith("{"):
    end = (i for i, v in enumerate(arguments) if v.endswith("}")).next()
    arguments = [{arg.lstrip("{").rstrip("}") for arg in arguments[0:end + 1]}] + arguments[end + 1:]

  arguments = [None if (arg == "null" or arg == "") else arg for arg in arguments]

  if isinstance(arguments[0], set):
    arguments[0] = [None if (arg == "null" or arg == "") else arg for arg in arguments[0]]

  return (command_name, arguments)


def MILK_parse(filename):
  """Parses a MILK XML file into a list of commands.

  Args:
    filename - a string

  Returns:
    A list of (command_name, args) tuples.
  """
  with open(filename, "r") as f:
    tree = etree.XML(f.read())

  unparsed_commands = [command.text for command in tree.findall(".//annotation")]

  commands = [MILK_parse_command(c) for c in unparsed_commands]

  return commands

def MILK_parse_originaltext(filename):
  """Parses a MILK XML file into a list of the original text lines. Contains
  duplicate lines so that the returned list can be zipped with the result from
  MILK_parse.

  Args:
    filename - a string

  Returns:
    A list of strings.
  """
  with open(filename, "r") as f:
    tree = etree.XML(f.read())
    return [ot.text for ot in tree.findall(".//originaltext")]
