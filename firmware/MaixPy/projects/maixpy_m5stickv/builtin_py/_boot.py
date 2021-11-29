import os
import sys
import time

banner = '''
 __  __              _____  __   __  _____   __     __
|  \/  |     /\     |_   _| \ \ / / |  __ \  \ \   / /
| \  / |    /  \      | |    \ V /  | |__) |  \ \_/ /
| |\/| |   / /\ \     | |     > <   |  ___/    \   /
| |  | |  / ____ \   _| |_   / . \  | |         | |
|_|  |_| /_/    \_\ |_____| /_/ \_\ |_|         |_|

M5StickV by M5Stack : https://m5stack.com/
M5StickV Wiki       : https://docs.m5stack.com
Co-op by Sipeed     : https://www.sipeed.com
'''
print(banner)

i = 1
while i < 10:
	if 'boot.py' in os.listdir():
		break
	time.sleep(i)
	i += 1
		
if 'boot.py' not in os.listdir():
	print('boot.py not found')
	sys.exit()
	
with open('boot.py') as f:
	exec(f.read())
sys.exit()
