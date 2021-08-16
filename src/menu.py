# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import lcd
from input import BUTTON_ENTER, BUTTON_PAGE

MENU_CONTINUE = const(0)
MENU_EXIT     = const(1)
MENU_SHUTDOWN = const(2)

class Menu:
	def __init__(self, ctx, menu):
		self.ctx = ctx
		self.menu = menu
		
	def run_loop(self):
		selected_item_index = 0
		while True:
			lcd.clear()
			self.draw_menu(selected_item_index)
			
			btn = self.ctx.input.wait_for_button(block=True)
			if btn == BUTTON_ENTER:
				try:
					lcd.clear()
					status = self.menu[selected_item_index][1]()
					if status != MENU_CONTINUE:
						return status
				except Exception as e:
					print(e)
					self.ctx.display.flash_text('Something went wrong', lcd.RED)
					lcd.clear()
					self.ctx.display.draw_centered_text(repr(e), lcd.RED)
					self.ctx.input.wait_for_button()
			elif btn == BUTTON_PAGE:
				selected_item_index = (selected_item_index + 1) % len(self.menu)
 
	def draw_menu(self, selected_item_index):
		menu_list = []
		for i, menu_item in enumerate(self.menu):
			menu_list_item = menu_item[0]
			if selected_item_index == i:
				lines = menu_item[0].split('\n')
				menu_list_item = '- ' + lines[0] + ' -' + ('\n' + '\n'.join(lines[1:]) if len(lines) > 1 else '')
			menu_list.append(menu_list_item)
		self.ctx.display.draw_centered_text('\n\n'.join(menu_list))
				