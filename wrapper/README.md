# Wrapper

Tracking wine games is difficult because wine spawns it's own subprocesses and PyAutoSplit isn't directly allowed to track them.
As a workaround there's a little wrapper binary which allows to track abritary executables with elevated user rights.

Make sure that the pyautosplit script and all related scripts like python-ptrace **can't be altered** by something malicious. This script will have **elevated user rights** and will be able to **read all memory**. One way to ensure this is by installing PyAutoSplit system-wide.

## Build and install the wrapper binary

1. Install developement dependency equivalents for your distribution:
    * [`meson`](https://repology.org/project/meson/versions)
    * [`ninja`](https://repology.org/project/ninja/versions)
    * [`python`](https://repology.org/project/python/versions)
    * C compiler like [`gcc`](https://repology.org/project/gcc/versions)
1. Build the wrapper binary:
    1.  Create a new directory for building:

        ~~~ sh
        meson setup builddir --buildtype release
        ~~~
    1.  Optional:
        * Configure the absolute path to PyAutoSplit. The default is `/usr/local/bin/pyautosplit` where PyAutoSplit gets installed system-wide by default and can't be altered without root permissions.

          ~~~ sh
          meson configure builddir -Dpyautosplit='/usr/local/bin/pyautosplit'
          ~~~
    1.  Compile the binary:

        ~~~ sh
        meson compile -C builddir
        ~~~
    1.  Install the binary. The default is `/usr/local/bin/pyautosplit-wrapper` which can't be altered without root permissions.

        ~~~ sh
        meson install -C builddir
        ~~~
1.  Allow this specific binary to read memory from all processes. This requires root privileges.
    ~~~ sh
    setcap cap_sys_ptrace=ep /usr/local/bin/pyautosplit-wrapper
    ~~~

## Configure

Set the executable name in your `gamefile.json`. The name should match the executable exactly.

## Run

Start PyAutoSplit as usual but replace `pyautosplit` with `pyautosplit-wrapper`:
~~~ sh
pyautosplit-wrapper -f livesplitone -- routefile.json
~~~
