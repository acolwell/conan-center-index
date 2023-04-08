from conan import ConanFile, Version
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv

import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        ms = VirtualRunEnv(self)
        ms.generate()

        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        version = Version(self.dependencies["openimageio"].ref.version)
        tc.variables["CMAKE_CXX_STANDARD"] = 14 if version >= "2.3.0.0" else 11
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
