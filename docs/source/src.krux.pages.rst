📜 src.krux.pages package
==========================

..  module:: src.krux.pages
   :synopsis: Subpackages and Submodules for ``src.krux.pages`` UI 
   :platform: RISC-V K210

.. moduleauthor:: Jeff Sun

The ``krux`` UX model is list-based: each screen is a simple vertical list
of large, tap-friendly items. Each item triggers an action (navigate, capture,
confirm, input, etc.). Chaining multiple list screens builds a full UX while
avoiding crowded screens with many tiny buttons.

1) One screen = one list

.. code-block:: bash

      .---------------------------------------.
      |                                       |
      |                                [||||] | # (battery icon)
      |---------------------------------------|
      |                                       |
      |               Item 1                  |
      |---------------------------------------|
      |                                       |
      |               Item 2                  |
      |---------------------------------------|
      |                                       |
      |               Item 3                  |
      |---------------------------------------|
      |                                       |
      |               Item 4                  |
      |                                       |
      '---------------------------------------'

2) Each item can lead to another list screen or an action

.. code-block:: bash

      .---------------------------------------.
      |                                       |
      |                                [||||] |
      |---------------------------------------|
      |                                       |
      |     Item 1  ->  another list (menu)   |
      |---------------------------------------|
      |                                       |
      |     Item 2  ->  capture image / scan  |
      |---------------------------------------|
      |                                       |
      |     Item 3  ->  wait touch / gesture  |
      |---------------------------------------|
      |                                       |
      |     Item 4  ->  load / show words     |
      |                                       |
      '---------------------------------------'

3) UX = a chain of list screens (spread items across steps)

.. code-block:: bash

      .---------------------------------------.          .---------------------------------------.
      |                                       |          |                                       |
      |                                [||||] |          |                                [||||] |
      |---------------------------------------|          |---------------------------------------|
      |                                       |          |                                       |
      |              Load key                 | ======>  |              From QR                  |
      |---------------------------------------|          |---------------------------------------|
      |                                       |          |                                       |
      |             Create key                |          |             From Camera               |
      |---------------------------------------|          |---------------------------------------|
      |                                       |          |                                       |
      |               Tools                   |          |              From Words               |
      |---------------------------------------|          |---------------------------------------|
      |                                       |          |                                       |
      |             Settings                  |          |                Back                   |
      |                                       |          |                                       |
      '---------------------------------------'          '---------------------------------------'

4) Maybe we can have more info besides battery,
like the used bitcoin network and wallet fingerprint:

.. code-block:: bash

      .---------------------------------------.
      |                                       |
      |  main         a3f97c2d          [||||]|
      |---------------------------------------|
      |                                       |
      |              Backup key               |
      |---------------------------------------|
      |                                       |
      |            Load descriptor            |
      |---------------------------------------|
      |                                       |
      |               Customize               |
      |---------------------------------------|
      |                                       |
      |                 Sign                  |
      |                                       |
      '---------------------------------------'



.. warning:: 

  Key ideas: keep each screen short and clear (few big items); spread many
  options across multiple screens (a chain); the chain of UIs constructs
  the UX for a purpose (load a key, create a key, etc.).

.. automodule:: src.krux.pages
   :members:
   :show-inheritance:
   :undoc-members:

Subpackages
-----------

.. toctree::
   :maxdepth: 1

   src.krux.pages.home_pages
   src.krux.pages.new_mnemonic

Submodules
----------

.. toctree::
   :maxdepth: 1

   src.krux.pages.capture_entropy
   src.krux.pages.datum_tool
   src.krux.pages.device_tests
   src.krux.pages.encryption_ui
   src.krux.pages.file_manager
   src.krux.pages.file_operations
   src.krux.pages.fill_flash
   src.krux.pages.flash_tools
   src.krux.pages.keypads
   src.krux.pages.login
   src.krux.pages.mnemonic_editor
   src.krux.pages.mnemonic_loader
   src.krux.pages.print_page
   src.krux.pages.qr_capture
   src.krux.pages.qr_view
   src.krux.pages.screensaver
   src.krux.pages.settings_page
   src.krux.pages.stack_1248
   src.krux.pages.tc_code_verification
   src.krux.pages.tiny_seed
   src.krux.pages.tools
   src.krux.pages.utils
   src.krux.pages.wallet_settings
