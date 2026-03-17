{
  description = "Krux flake";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312;
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.poetry
            pkgs.docker
            pkgs.openssl
            pkgs.wget
            pkgs.git
            pkgs.pkg-config
            pkgs.screen
            pkgs.zlib
            pkgs.libffi
            pkgs.stdenv.cc.cc.lib
            pkgs.cairo
            pkgs.glib
            pkgs.gtk3
            pkgs.gobject-introspection
            pkgs.freetype
            pkgs.fontconfig
            pkgs.pango
            pkgs.gdk-pixbuf
            pkgs.atk
            pkgs.libGL
            pkgs.libpng
            pkgs.libjpeg
            pkgs.dbus
            pkgs.SDL2
            pkgs.SDL2_image
            pkgs.SDL2_mixer
            pkgs.SDL2_ttf
            pkgs.mtdev
            pkgs.xorg.libX11
            pkgs.xorg.libXext
            pkgs.xorg.libXrender
            pkgs.xorg.libxcb
            pkgs.xorg.libXrandr
            pkgs.xorg.libXinerama
            pkgs.xorg.libXcursor
            pkgs.xorg.libXi
            pkgs.xorg.libXxf86vm
            pkgs.zbar
            pkgs.libusb1
            pkgs.polkit
            pkgs.shadow
            pkgs.tcl
            pkgs.tk
          ];

          shellHook = ''
            # Set up proper directories for Poetry and Python
            export HOME="''${HOME:-$(pwd)/.home}"
            export XDG_DATA_HOME="$HOME/.local/share"
            export XDG_CONFIG_HOME="$HOME/.config"
            export XDG_CACHE_HOME="$HOME/.cache"

            # Create necessary directories
            mkdir -p "$HOME" "$XDG_DATA_HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"

            # Poetry configuration
            export POETRY_CACHE_DIR="$XDG_CACHE_HOME/pypoetry"
            export POETRY_DATA_DIR="$XDG_DATA_HOME/pypoetry"
            export POETRY_CONFIG_DIR="$XDG_CONFIG_HOME/pypoetry"
            export POETRY_VENV_PATH="$POETRY_CACHE_DIR/virtualenvs"

            # Create Poetry directories
            mkdir -p "$POETRY_CACHE_DIR" "$POETRY_DATA_DIR" "$POETRY_CONFIG_DIR" "$POETRY_VENV_PATH"

            # Python and virtual environment setup
            export VIRTUAL_ENV_DISABLE_PROMPT=1
            export PIP_CACHE_DIR="$XDG_CACHE_HOME/pip"
            mkdir -p "$PIP_CACHE_DIR"

            # pyzbar calls cdll.LoadLibrary(find_library("zbar")) which resolves to
            # the bare soname "libzbar.so.0". NixOS dlopen cannot find bare sonames
            # since there is no ldconfig cache. pyzbar has no env var override, so
            # we patch its zbar_library.py in the venv to use the absolute store path.
            VENV_PATH=$(poetry env info --path 2>/dev/null)
            if [ -n "$VENV_PATH" ]; then
              PYZBAR_LIB=$(find "$VENV_PATH" -name "zbar_library.py" 2>/dev/null | head -1)
              if [ -n "$PYZBAR_LIB" ]; then
                # Replace both the original find_library call AND any previously
                # patched (possibly stale) store path with the current correct one.
                sed -i "s|path = find_library('zbar')|path = '${pkgs.zbar.lib}/lib/libzbar.so'|g" "$PYZBAR_LIB"
                sed -i "s|path = '/nix/store/[^']*libzbar.so'|path = '${pkgs.zbar.lib}/lib/libzbar.so'|g" "$PYZBAR_LIB"
              fi
            fi

            # LD_LIBRARY_PATH: expose all native libs that Python packages
            # may dlopen at runtime (Kivy, pygame, zbar bindings, etc.)
            export LD_LIBRARY_PATH=\
            ${pkgs.libGL}/lib:\
            ${pkgs.stdenv.cc.cc.lib}/lib:\
            ${pkgs.xorg.libX11}/lib:\
            ${pkgs.xorg.libxcb}/lib:\
            ${pkgs.mtdev}/lib:\
            ${pkgs.zbar.lib}/lib:\
            ${pkgs.SDL2}/lib:\
            ${pkgs.SDL2_image}/lib:\
            ${pkgs.SDL2_mixer}/lib:\
            ${pkgs.SDL2_ttf}/lib:\
            ${pkgs.cairo}/lib:\
            ${pkgs.glib}/lib:\
            ${pkgs.glib.out}/lib:\
            ${pkgs.gtk3}/lib:\
            ${pkgs.pango}/lib:\
            ${pkgs.gdk-pixbuf}/lib:\
            ${pkgs.freetype}/lib:\
            ${pkgs.fontconfig.lib}/lib:\
            ${pkgs.zlib}/lib:\
            ${pkgs.libffi}/lib:\
            ${pkgs.libusb1}/lib:\
            ${pkgs.libpng}/lib:\
            ${pkgs.libjpeg}/lib:\
            ${pkgs.dbus.lib}/lib:\
            $LD_LIBRARY_PATH

            # GObject introspection typelibs — required for gi.repository (Kivy GTK backend)
            export GI_TYPELIB_PATH=\
            ${pkgs.gtk3}/lib/girepository-1.0:\
            ${pkgs.glib}/lib/girepository-1.0:\
            ${pkgs.pango}/lib/girepository-1.0:\
            ${pkgs.gdk-pixbuf}/lib/girepository-1.0:\
            ${pkgs.atk}/lib/girepository-1.0:\
            ''${GI_TYPELIB_PATH:+:$GI_TYPELIB_PATH}

            # pkg-config path so Poetry-built C extensions can find headers
            export PKG_CONFIG_PATH=\
            ${pkgs.zbar}/lib/pkgconfig:\
            ${pkgs.SDL2}/lib/pkgconfig:\
            ${pkgs.cairo}/lib/pkgconfig:\
            ${pkgs.gtk3}/lib/pkgconfig:\
            ''${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}

            export PYTHONPATH=$PWD/src:$PYTHONPATH

            # Force SDL2 to use XWayland — the Wayland backend does not render pygame windows
            export SDL_VIDEODRIVER=x11

            # Poetry run spawns a subprocess that may lose LD_LIBRARY_PATH.
            # Persist it into the venv's activate script so every `poetry run`
            # subprocess inherits the correct library paths.
            VENV_PATH=$(poetry env info --path 2>/dev/null)
            if [ -n "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/activate" ]; then
              # Remove any previous injection to avoid duplicates
              sed -i '/# nix-ld-inject/d' "$VENV_PATH/bin/activate"
              echo "export LD_LIBRARY_PATH="$LD_LIBRARY_PATH" # nix-ld-inject" >> "$VENV_PATH/bin/activate"
              echo "export GI_TYPELIB_PATH="$GI_TYPELIB_PATH" # nix-ld-inject" >> "$VENV_PATH/bin/activate"
            fi

            # Explicitly bind Poetry to the Nix-provided Python.
            export POETRY_PYTHON="${python}/bin/python3"
            poetry env use "${python}/bin/python3" 2>/dev/null || true

            # Configure Poetry to use local virtualenvs
            poetry config virtualenvs.in-project false
            poetry config virtualenvs.path "$POETRY_VENV_PATH"
            poetry config cache-dir "$POETRY_CACHE_DIR"

            echo "Krux development environment ready!\u2705"
            echo ""
            echo "=== Firmware ==="
            echo "  Build:  ./krux build maixpy_amigo"
            echo "  Flash:  ./krux flash maixpy_amigo"
            echo ""
            echo "=== Python dev ==="
            echo "  Install deps:      poetry install"
            echo "  Install simulator: poetry install --extras simulator"
            echo "  Install all:       poetry install --all-extras"
            echo "  Run tests:         poetry run poe test"
            echo "  Lint:              poetry run poe lint"
            echo "  Format:            poetry run poe format"
            echo ""
            echo "=== i18n ==="
            echo "  poetry run poe i18n clean"
            echo "  poetry run poe i18n new <locale>"
            echo "  poetry run poe i18n fill"
            echo "  poetry run poe i18n validate"
            echo "  poetry run poe i18n prettify"
            echo "  poetry run poe i18n bake"
            echo ""
            echo "=== Simulator ==="
            echo "  poetry run poe simulator"
            echo "  poetry run poe simulator-m5stickv"
            echo "  poetry run poe simulator-dock"
            echo "  poetry run poe simulator-yahboom"
            echo "  poetry run poe simulator-cube"
            echo "  poetry run poe simulator-wonder-mv"
            echo "  poetry run poe simulator-tzt"
            echo ""
            echo "=== Serial debug ==="
            echo "  screen /dev/ttyUSB0 115200"
            echo ""
            echo "NOTE: Add to your configuration.nix:"
            echo "  users.users.<youruser>.extraGroups = [ \"dialout\" \"docker\" ];"
            echo "  Then reboot."
          '';
        };
      }
    );
}