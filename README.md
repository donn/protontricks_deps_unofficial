> This is an unofficial distribution of the underlying utilties. Please do not
> bug protontricks, winetricks, or cabextract if you run into issues using
> these binaries.

# `protontricks_deps_unofficial`

These are unofficial binary wheels for the dependencies of
[protontricks](https://pypi.org/project/protontricks/): namely, the `winetricks`
script and transitively `cabextract`.

# Why?

SteamOS is immutable and I didn't in fact want to download a ≈1 GiB flatpak for
a Python script and a shell script so I made a `venv` in my home directory only
to realize I need to compile `cabextract` on another computer and then copy it
to my home directory.

This just lets me install them via PIP.

# Usage

## First time

```bash
python3 -m venv venv
source ./venv/bin/activate
VERSION=2026.01.25
pip3 install --upgrade protontricks https://github.com/donn/protontricks_deps_unofficial/releases/download/$VERSION/protontricks_deps_unofficial-$VERSION-py3-none-manylinux2014_$(uname -m).manylinux_2_17_$(uname -m).whl
```

## Subsequent Uses

```bash
source ./venv/bin/activate
protontricks […]
```

# Legal Info

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

Licenses for distributed binaries:

## Winetricks

Copyright (C) 2014 Dan Kegel

Copyright (C) 2016 Austin English

This software comes with ABSOLUTELY NO WARRANTY.

This is free software, placed under the terms of the GNU Lesser
Public License version 2.1 (or later), as published by the Free
Software Foundation. Please see the file [COPYING](./winetricks-COPYING) for
details.

## cabextract

(C) 2000-2023 Stuart Caie <kyzer@cabextract.org.uk>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received
[a copy of the GNU General Public License](./cabextract-COPYING)
along with this program if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
