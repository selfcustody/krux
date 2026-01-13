📦 src package
==============

..  module:: src
   :synopsis: Source package for ``krux``
   :platform: RISC-V K210

.. moduleauthor:: Jeff Sun

🥾 src.boot
-----------

``src.boot`` is a simple module and have few methods to boot the device with
a firmware capable of sign messages, PSBTs and more.

🧙🏼‍♂️ src.krux
-----------

``src.krux`` has a lot of submodules and subpackages. The easiest way to start
is through ``src.krux.pages.login`` and ``src.krux.pages.home``, that are called
in ``src.boot.on_run`` method and you can explore through experimenting on UI/UX.

.. automodule:: src
   :members:
   :show-inheritance:
   :undoc-members:

.. toctree::
   :maxdepth: 2

   src.boot
   src.krux
