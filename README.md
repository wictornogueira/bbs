# BBS

A (hopefully) game agnostic* minimalistic mod loader that enables python scripting

\* 32-bit games only  
\* Ultimate ASI Loader compatible games only  
\* Not tested :)

## Installation

1. Install ASI loader
2. Get the latest version [here](https://github.com/wictornogueira/bbs/releases/latest/download/bbs.zip)
3. Extract all files to your game directory
4. Install the [hooking plugin](/hooks/) corresponding to your game

## Usage

- Drop your plugins into `scripts/bbs/plugins` and you should be ready to go
- You might also want to reload your plugins during runtime, in which you case, all you have to do is press `[` (ANSI) or `´` (ISO) -- requires hook

## Writing your own plugin

First of all, create a python file which can be named whatever you like.  
Then, create a class; once again, you can name it whatever you like, just don't forget to decorate it using `@bbsplugin`.  
The class you have just now created may or may not implement three methods called `onLoad`, `onUnload` and `onUpdate` which will be called at different times as shown bellow.

```python
@bbsplugin
class ExamplePlugin:
  def onLoad (self):
    # Called during loading
    self.print("Loading :)")

  def onUnload (self):
    # Called during unloading
    self.print("Unloading :(")

  def onUpdate (self):
    # Called once per frame -- requires hook
    self.print("Console spam goes brrr")
```

You may have noticed the use of a method called `print`, it's one of BBS' provided methods.  
Here's some of the methods provided by BBS:

```python
print(*args) -> None
debugPrint(*args) -> None
initConsole() -> None
destroyConsole() -> None
toggleConsole() -> bool
isKeyPressed(key: int) -> bool
readMem(addr: int, items: int = 1, size: int = 1) -> int[]
writeMem(addr: int, buff: int[], size: int = 1) -> int[]
makeCall(at: int, to: int) -> None
```

In case you need access to foreign functions or classes, take a look at [ctypes](https://docs.python.org/3/library/ctypes.html).  
