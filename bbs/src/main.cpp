#include <windows.h>
#include <string>
#include <iostream>
#include <pybind11/embed.h>
#include <pybind11/stl.h>

namespace py = pybind11;

void initConsole() {
  if (AllocConsole()) {
    FILE* fDummy;
    freopen_s(&fDummy, "CONIN$", "r", stdin);
    freopen_s(&fDummy, "CONOUT$", "w", stderr);
    freopen_s(&fDummy, "CONOUT$", "w", stdout);
  }
}

void destroyConsole() {
  FreeConsole();
}

void print(py::str text) {
  std::cout << text << std::endl;
}

void writeToMem(size_t at, py::list& buff, size_t length) {
  DWORD oldvp;
  size_t addr = at;

  VirtualProtect((LPVOID)at, length, PAGE_EXECUTE_READWRITE, &oldvp);

  for (size_t i = 0; i < length; i++) {
    *((std::uint8_t*)addr) = buff[i].cast<std::uint8_t>();
    addr++;
  }

  VirtualProtect((LPVOID)at, 5, oldvp, &oldvp);
}

void readFromMem(size_t at, py::list& buff, size_t length) {
  DWORD oldvp;
  size_t addr = at;

  VirtualProtect((LPVOID)at, length, PAGE_EXECUTE_READWRITE, &oldvp);

  for (size_t i = 0; i < length; i++) {
    buff.append(*(std::uint8_t*)addr);
    addr++;
  }

  VirtualProtect((LPVOID)at, 5, oldvp, &oldvp);
}

void makeCall(size_t at, size_t to) {
  DWORD oldvp;
  VirtualProtect((LPVOID)at, 5, PAGE_EXECUTE_READWRITE, &oldvp);
  
  *((std::uint8_t*)at) = 0xE8;
  *((uint32_t*)++at) = (uint32_t)to - (at + 4);

  VirtualProtect((LPVOID)--at, 5, oldvp | PAGE_EXECUTE, &oldvp);
 }

void exec(const char *s) {
  try {
    py::exec(s);
  }
  catch (py::error_already_set& e) {
    initConsole();
    std::cout << e.what() << std::endl;
  }
  catch (...) {
    initConsole();
    std::cout << "Error" << std::endl;
  }
}

void mainLoop() {
  exec(R"(
BBS.handler.update()
  )");
}

bool isKeyPressed(size_t key) {
  return GetAsyncKeyState(key) & 0b1;
}

PYBIND11_EMBEDDED_MODULE(BBS, m) {
  m.def("writeToMem", &writeToMem);
  m.def("readFromMem", &readFromMem);
  m.def("print", &print);
  m.def("initConsole", &initConsole);
  m.def("destroyConsole", &destroyConsole);
  m.def("makeCall", &makeCall);
  m.def("isKeyPressed", &isKeyPressed);
  m.attr("mainLoopAddr") = (size_t)&mainLoop;
}

void init() {
  py::initialize_interpreter();
  exec(R"(
import BBS
import bbs.bootstrapper
  )");
}

void exit() {
  exec(R"(
BBS.handler.unloadAllModules()
  )");
  py::finalize_interpreter();
  destroyConsole();
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
  switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
      init();
      break;
    case DLL_PROCESS_DETACH:
      exit();
      break;
  }

  return 1;
}
