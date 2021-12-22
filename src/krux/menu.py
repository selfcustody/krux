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
from .input import BUTTON_ENTER, BUTTON_PAGE

MENU_CONTINUE = 0
MENU_EXIT     = 1
MENU_SHUTDOWN = 2

class Menu:
    """Represents a menu that can render itself to the screen, handle item selection,
       and invoke menu item callbacks that return a status
    """

    def __init__(self, ctx, menu):
        self.ctx = ctx
        self.menu = menu

    def run_loop(self):
        """Runs the menu loop until one of the menu items returns either a MENU_EXIT
           or MENU_SHUTDOWN status
        """
        selected_item_index = 0
        while True:
            self.ctx.display.clear()
            self._draw_menu(selected_item_index)

            btn = self.ctx.input.wait_for_button(block=True)
            if btn == BUTTON_ENTER:
                try:
                    self.ctx.display.clear()
                    status = self.menu[selected_item_index][1]()
                    if status != MENU_CONTINUE:
                        return (selected_item_index, status)
                except Exception as e:
                    self.ctx.log.exception(
                        'Exception occurred in menu item "%s"' % self.menu[selected_item_index][0]
                    )
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(( 'Error:\n%s' ) % repr(e), lcd.RED)
                    self.ctx.input.wait_for_button()
            else:
                selected_item_index = (selected_item_index + 1) % len(self.menu)

    def _draw_menu(self, selected_item_index):
        menu_list = []
        for i, menu_item in enumerate(self.menu):
            menu_item_lines = self.ctx.display.to_lines(menu_item[0])
            if selected_item_index == i:
                selected_line = '- %s -' % menu_item_lines[0]
                if len(self.ctx.display.to_lines(selected_line)) > 1:
                    selected_line = '-%s-' % menu_item_lines[0]
                menu_item_lines[0] = selected_line
            menu_list_item = menu_item_lines[0]
            if len(menu_item_lines) > 1:
                menu_list_item += '\n' + '\n'.join(menu_item_lines[1:])
            menu_list.append(menu_list_item)
        self.ctx.display.draw_centered_text(
            '\n\n'.join(menu_list),
            color=lcd.WHITE,
            word_wrap=False
        )
