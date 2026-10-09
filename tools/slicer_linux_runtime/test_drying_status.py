#!/usr/bin/env python3
"""Compile the production status-label function with UI stubs, without hardware."""
from pathlib import Path
import os
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / 'src/slic3r/GUI/AMSDryControl.cpp').read_text()
a = src.index('void AMSDryCtrWin::update_img_description(')
b = src.index('int AMSDryCtrWin::update_image(', a)
body = src[a:b]
prelude = r'''
#include <string>
#include <iostream>
#include <stdexcept>
using wxString = std::string;
#define _L(x) std::string(x)
#define BOOST_LOG_TRIVIAL(x) std::cerr
struct Exception {};
struct DevAms {
 enum class DryStatus : char { Off, Checking, Drying, Cooling, Stopping, Error, CannotStopHeatOutofControl, PrdTesting };
 enum class DrySubStatus { Off, Heating, Dehumidify };
};
struct Label {
 std::string text = "Idle";
 void SetLabel(const std::string& s) { text = s; }
 const std::string& GetLabel() const { return text; }
};
struct Icon { void Show(bool) {} void SetBitmap(int) {} };
struct ScalableBitmap {
 ScalableBitmap() = default;
 ScalableBitmap(void*, const char*, int) {}
 void msw_rescale() {} int bmp() { return 0; }
};
struct AMSDryCtrWin {
 Label label;
 Icon icon;
 Label* m_image_description = &label;
 Icon* m_image_description_icon = &icon;
 ScalableBitmap m_description_icon_bitmap;
 void update_img_description(DevAms::DryStatus, DevAms::DrySubStatus);
};
'''
cases = r'''
int main() {
 using S = DevAms::DryStatus; using U = DevAms::DrySubStatus;
 AMSDryCtrWin ui;
 struct Case { S status; U sub; const char* expected; };
 Case cases[] = {
  {S::Off,U::Off,"Idle"},
  {S::Drying,U::Off,"Drying"},
  {S::Drying,U::Heating,"Drying-Heating"},
  {S::Drying,U::Dehumidify,"Drying-Dehumidifying"},
  {S::Cooling,U::Off,"Cooling down"},
  {S::Checking,U::Off,"Checking drying conditions"},
  {S::Stopping,U::Off,"Stopping"},
  {S::Error,U::Heating,"Drying Error"},
  {S::CannotStopHeatOutofControl,U::Off,"Heating fault: check the AMS display"},
  {static_cast<S>(15),U::Off,"Unknown drying status"},
  {S::Drying,static_cast<U>(3),"Drying"},
  {S::Off,U::Off,"Idle"}
 };
 for (const auto& c : cases) {
  ui.update_img_description(c.status,c.sub);
  if (ui.label.text != c.expected) throw std::runtime_error("Incorrect drying status label");
 }
 std::cout << "12 drying status transitions passed\n";
}
'''
with tempfile.TemporaryDirectory(prefix='dry-status-') as tmp:
    cpp = Path(tmp) / 'test.cpp'
    exe = Path(tmp) / 'test'
    cpp.write_text(prelude + body + cases)
    subprocess.run([os.environ.get('CXX', 'g++'), '-std=c++17', '-Wall', '-Wextra', str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
