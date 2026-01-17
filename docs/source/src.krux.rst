🧙🏼‍♂️ src.krux package
====================

..  module:: src.boot
   :synopsis: Subpackages and Submodules for ``krux``
   :platform: RISC-V K210

.. moduleauthor:: Jeff Sun

The ``src.krux`` package is the brain while ``src.boot`` is the hearth. Here
you can deal with hardware specifics (like ``src.krux.printers``) or/and
aesthetic themes, like ``src.krux.themes``.

.. automodule:: src.krux
   :members:
   :show-inheritance:
   :undoc-members:

🗳️ Subpackages
--------------

.. toctree::
   :maxdepth: 1

   src.krux.pages
   src.krux.printers
   src.krux.touchscreens
   src.krux.translations

.. warning::
   the module ``src.krux.translations`` and related files on ``i18n/*`` should
   be treated with some caution. Adding new translations will increase the firmware.

🧩 Submodules
-------------

.. toctree::
   :maxdepth: 1

   src.krux.auto_shutdown
   src.krux.baseconv
   src.krux.bbqr
   src.krux.bip39
   src.krux.buttons
   src.krux.camera
   src.krux.context
   src.krux.display
   src.krux.encryption
   src.krux.firmware
   src.krux.format
   src.krux.i2c
   src.krux.input
   src.krux.kboard
   src.krux.kef
   src.krux.key
   src.krux.krux_settings
   src.krux.light
   src.krux.metadata
   src.krux.power
   src.krux.psbt
   src.krux.qr
   src.krux.rotary
   src.krux.sats_vb
   src.krux.sd_card
   src.krux.settings
   src.krux.themes
   src.krux.touch
   src.krux.wallet
   src.krux.wdt
