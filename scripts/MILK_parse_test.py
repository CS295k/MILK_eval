import unittest
from MILK_parse import MILK_parse_command

class TestMILK_parse(unittest.TestCase):

	def test_command_correct_start(self):
		self.assertEqual(MILK_parse_command("command(\"chicken\", ing0)"),
											("command", ["chicken", "ing0"]))

	def test_command_null_description_start(self):
		self.assertEqual(MILK_parse_command("command(null, ing0)"),
											("command", [None, "ing0"]))

	def test_command_empty_description_start(self):
		self.assertEqual(MILK_parse_command("command(\"\", ing0)"),
											("command", [None, "ing0"]))

	def test_command_no_description_start(self):
		self.assertEqual(MILK_parse_command("command( , ing0)"),
											("command", [None, "ing0"]))

	def test_command_correct_mid(self):
		self.assertEqual(MILK_parse_command("command(ing0, \"chicken\", t0)"),
											("command", ["ing0", "chicken", "t0"]))

	def test_command_null_description_mid(self):
		self.assertEqual(MILK_parse_command("command(ing0, null, t0)"),
											("command", ["ing0", None, "t0"]))

	def test_command_empty_description_mid(self):
		self.assertEqual(MILK_parse_command("command(ing0, \"\", t0)"),
											("command", ["ing0", None, "t0"]))

	def test_command_no_description_mid(self):
		self.assertEqual(MILK_parse_command("command(ing0, , t0)"),
											("command", ["ing0", None, "t0"]))

	def test_command_correct_end(self):
		self.assertEqual(MILK_parse_command("command(ing0, \"chicken\")"),
											("command", ["ing0", "chicken"]))

	def test_command_null_description_end(self):
		self.assertEqual(MILK_parse_command("command(ing0, null)"),
											("command", ["ing0", None]))

	def test_command_empty_description_end(self):
		self.assertEqual(MILK_parse_command("command(ing0, \"\")"),
											("command", ["ing0", None]))

	def test_command_no_description_end(self):
		self.assertEqual(MILK_parse_command("command(ing0, )"),
											("command", ["ing0", None]))

	def test_command_set(self):
		self.assertEqual(MILK_parse_command("command({ing1, ing2}, ing0)"),
											("command", [["ing1", "ing2"], "ing0"]))

	def test_command_empty_set(self):
		self.assertEqual(MILK_parse_command("command({}, ing0)"),
											("command", [[None], "ing0"]))

	def test_command_null_set(self):
		self.assertEqual(MILK_parse_command("command({null}, ing0)"),
											("command", [[None], "ing0"]))

	def test_command_empty_string_set(self):
		self.assertEqual(MILK_parse_command("command({\"\"}, ing0)"),
											("command", [[None], "ing0"]))

if __name__ == "__main__":
	unittest.main()