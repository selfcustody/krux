src.boot module
===============

..  module:: src.boot
   :synopsis: Boot sequence for Krux devices
   :platform: Linux, MacOS, Windows

.. moduleauthor:: Jeff

The boot module handles the initial startup sequence for Krux hardware devices.

..  warning::
   This module requires hardware-specific dependencies and cannot be fully 
   auto-documented in a standard Python environment. 

Overview
--------

The ``src/boot.py`` module is the entry point when a Krux device powers on. It:

1. Initializes the display hardware
2. check for firmware updates and forbid to do downgrades;
3. initial garbage collection;
4. check for ``tc_code_verification``;
5. Launches the main application (`login` and `home` methods).

This is made through 5 methods:

- ``src.krux.on_preimport_ticks``;
- ``src.krux.on_postimport_ticks``;
- ``src.krux.on_tc_code_verification``;
- ``src.krux.on_run``;
- ``src.krux.on_shutdown``

You can check them at the end of ``src/boot.py``:

.. code-block:: python

    preimport_ticks = on_preimport_ticks()

    ctx.power_manager = power_manager
    auto_shutdown.add_ctx(ctx)

    on_postimport_ticks(preimport_ticks)
    on_tc_code_verification(power_manager)
    on_run()
    on_shutdown()


Functions
---------

.. py:function:: check_for_updates()

   Checks SD card, if a valid firmware is found asks if user wants to update the device.

.. py:function:: draw_splash()

   Draws the Krux splash screen on the device display during boot.

.. py:function:: login(ctx_login)
 
   Loads and run the Login page.

.. py:function:: home(ctx_home)

    Loads and run the Login page.

.. py:function:: main()

   Main entry point that initializes all hardware and starts the application loop.

.. py:function:: on_preimport_ticks()

   Draw K logo, check for new firmare and make garbage collector work.

.. py:function:: on_postimport_ticks(pt)

   If importing happened too fast, sleep the difference so the logo will be shown.

.. py:function:: on_tc_code_verification(pm)

   Check for TC_CODE and if it fails, shutdown the device.

.. py:function:: on_run()

    Basic architecture of krux:

    - Runs ``src.krux.pages.login.Login`` page;
    - cleans memory calling ``garbage.collect``;
    - runs ``src.krux.pages.home.Home`` page.

.. code-block:: python

    login(ctx)
    gc.collect()
    home(ctx)

.. py:function:: on_shutdown()

   Clear the current ``src.krux.context.Context`` and calls ``power_manager.shutdown``.

.. py:function:: tc_code_verification(ctx_pin)

   Loads and run the Pin Verification page.
