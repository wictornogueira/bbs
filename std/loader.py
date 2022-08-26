import BBS
import os
import importlib

class PluginHandler:
  def __init__ (self, BBS):
    self.m_modules = {}
    self.m_BBS = BBS
    self.m_prevKeyState = 0

  def loadModule (self, name, pkg):
    module = importlib.import_module(name, pkg)

    if name in self.m_modules:
      self.m_modules[module.__name__]["module"] = module
    else:
      self.m_modules[name] = {
        "module": module,
        "plugins": {}
      }

    return self.m_modules[module.__name__]

  def loadPlugin (self, pluginClass):
    if pluginClass.__module__ not in self.m_modules:
      self.m_modules[pluginClass.__module__] = {
        "module": None,
        "plugins": {}
      }

    if pluginClass.__name__ in self.m_modules[pluginClass.__module__]["plugins"]:
      raise Exception("Plugin already loaded")

    pluginInstance = self.injectStd(pluginClass())

    self.m_modules[pluginClass.__module__]["plugins"][pluginClass.__name__] = pluginInstance
    getattr(pluginInstance, "onLoad", lambda *args: None)()
    return (pluginInstance, pluginClass)

  def unloadPlugin (self, pluginName):
    for module in self.m_modules:
      if pluginName in self.m_modules[module]["plugins"]:
        plugin = self.m_modules[module]["plugins"].pop(pluginName)
        return getattr(plugin, "onUnload", lambda *args: None)()

  def injectStd (self, pluginInstance):
    for prop in dir(self.m_BBS):
      if not prop.startswith("_"):
        if prop.startswith("i_"):
          setattr(pluginInstance, prop[2:], getattr(self.m_BBS, prop)(pluginInstance))
          continue

        setattr(pluginInstance, prop, getattr(self.m_BBS, prop))

    return pluginInstance

  def unloadModule (self, moduleName):
    if moduleName in self.m_modules:
      module = self.m_modules[moduleName]
      for plugin in list(module["plugins"].keys()):
        self.unloadPlugin(plugin)

      return module

  def reloadModule (self, moduleName):
    module = self.unloadModule(moduleName)
    if module and module["module"]:
      importlib.reload(module["module"])

  def reloadAllModules (self):
    for module in list(self.m_modules.keys()):
      self.reloadModule(module)

  def unloadAllModules (self):
    for module in self.m_modules:
      self.unloadModule(module)

  def getPlugin (self, pluginName, moduleName = None):
    if moduleName:
      if moduleName in self.m_modules:
        if pluginName in self.m_modules[moduleName]["plugins"]:
          return self.m_modules[moduleName]["plugins"][pluginName]

      return

    for module in self.m_modules:
      if pluginName in self.m_modules[module]["plugins"]:
        return self.m_modules[module]["plugins"][pluginName]

  def callAll (self, methodName, *args):
    for module in self.m_modules:
      for plugin in self.m_modules[module]["plugins"]:
        getattr(self.m_modules[module]["plugins"][plugin], methodName, lambda *args: None)(*args)

  def update (self):
    currState = self.m_BBS.isKeyPressed(0xDB)
    if currState != self.m_prevKeyState:
      if currState:
        self.reloadAllModules()

      self.m_prevKeyState = currState

    if self.m_BBS.isKeyPressed(0xC0):
      self.m_BBS.toggleConsole()

    self.callAll("onUpdate")

class EventDispatcher:
  def __init__ (self):
    self.handlers = {}

  def on (self, event, handler):
    if event not in self.handlers:
      self.handlers[event] = [handler]
      return

    self.handlers[event].append(handler)

  def dispatch (self, event, *args):
    if event not in self.handlers:
      return

    for handler in self.handlers[event]:
      handler(*args)

class StdMethods:
  s_console = False
  s_BBS = None
  s_consoleBacklog = []

  @classmethod
  def _setBBS (cls, BBS):
    cls.s_BBS = BBS

  @classmethod
  def initConsole (cls):
    if not cls.s_console:
      cls.s_BBS.initConsole()
      cls.s_console = True
      
      for line in cls.s_consoleBacklog:
        cls.s_BBS.print(line)

  @classmethod
  def destroyConsole (cls):
    if cls.s_console:
      cls.s_BBS.destroyConsole()
      cls.s_console = False

  @classmethod
  def toggleConsole (cls):
    cls.destroyConsole() if cls.s_console else cls.initConsole()
    return cls.s_console

  @classmethod
  def i_debugPrint (cls, pluginInstance):
    def debugPrint (*args):
      line = f"[{pluginInstance.__class__.__name__}] " + " ".join(map(lambda s: str(s), args))
      return cls.s_consoleBacklog.append(line)

    return debugPrint

  @classmethod
  def i_print (cls, pluginInstance):
    def print (*args):
      cls.initConsole()

      return cls.s_BBS.print(f"[{pluginInstance.__class__.__name__}] " + " ".join(map(lambda s: str(s), args)))

    return print

  @classmethod
  def readMem (cls, addr, items = 1, size = 1):
    buff = []
    cls.s_BBS.readFromMem(addr, buff, items * size)
    newBuff = [0] * items
    for i in range(items):
      for j in range(size):
        newBuff[i] += buff[i*j+j] << 0x8 * j

    return newBuff

  @classmethod
  def writeMem (cls, addr, buff, size = 1):
    newBuff = [0] * len(buff) * size
    for i in range(len(buff)):
      for j in range(size):
        newBuff[i*j+j] = (buff[i] >> 0x8 * j) & 0xFF

    cls.s_BBS.writeToMem(addr, newBuff, len(newBuff))
    return newBuff

  @classmethod
  def makeCall (cls, at, to):
    cls.s_BBS.makeCall(at, to)

  @classmethod
  def isKeyPressed (cls, key):
    return cls.s_BBS.isKeyPressed(key)

def main ():
  __builtins__['bbsplugin'] = lambda m: BBS.handler.loadPlugin(m)[1]

  StdMethods._setBBS(BBS)
  BBS.handler = PluginHandler(StdMethods)
  BBS_DIR = os.path.dirname(os.path.abspath(__file__))
  BBS_PLUGINS_DIR = os.path.join(BBS_DIR, "plugins")

  if (not os.path.isdir(BBS_PLUGINS_DIR)):
    os.mkdir(BBS_PLUGINS_DIR)

  for module in os.listdir(BBS_PLUGINS_DIR):
    if module.startswith("_") or not module.endswith(".py"):
      continue

    BBS.handler.loadModule(f"plugins.{module[:-3]}", module[:-3])

main()
