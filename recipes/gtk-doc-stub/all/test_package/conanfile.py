from conan import ConanFile
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout

import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac",
    test_type = "explicit"


    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if getattr(self, "settings_build", self.settings).os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.build_requires("msys2/cci.latest")
        self.build_requires("automake/1.16.4")

    def layout(self):
        basic_layout(self)

    def generate(self):
        ms = VirtualBuildEnv(self)
        ms.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src),
                        os.path.join(self.build_folder, src))
        autotools = Autotools(self)
        autotools.autoreconf(args=["-fiv"])
        args = [
            "--enable-option-checking=fatal",
            "--enable-gtk-doc=no",
        ]
        autotools.configure(args=args)

    def test(self):
        self.run("gtkdocize --copy", env="conanrun")
