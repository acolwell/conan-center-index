from conan import ConanFile, Version
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc
import functools
import os

required_conan_version = ">=1.45.0"


class OpenColorIOConan(ConanFile):
    name = "opencolorio"
    description = "A color management framework for visual effects and animation."
    license = "BSD-3-Clause"
    homepage = "https://opencolorio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("colors", "visual", "effects", "animation")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_sse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_sse": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if self.settings.arch not in ["x86", "x86_64"]:
            self.options.rm_safe("use_sse")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("expat/2.5.0")
        self.requires("yaml-cpp/0.7.0")
        if Version(self.version) < "2.0.0":
            self.requires("openexr/2.5.7")
            self.requires("tinyxml/2.6.2")
        else:
            self.requires("imath/3.1.6")
            self.requires("openexr/3.1.5")
            self.requires("pystring/1.1.3")
        # for tools only
        self.requires("lcms/2.14")
        # TODO: add GLUT (needed for ociodisplay tool)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

        apply_conandata_patches(self)

        for module in ("expat", "lcms2", "pystring", "yaml-cpp", "Imath"):
            rm(self, pattern="Find"+module+".cmake", folder=os.path.join(self.source_folder, "share", "cmake", "modules"), recursive=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)

        if Version(self.version) >= "2.1.0":
            tc.cache_variables["OCIO_BUILD_PYTHON"] = False
        else:
            tc.cache_variables["OCIO_BUILD_SHARED"] = self.options.shared
            tc.cache_variables["OCIO_BUILD_STATIC"] = not self.options.shared
            tc.cache_variables["OCIO_BUILD_PYGLUE"] = False
            tc.cache_variables["USE_EXTERNAL_YAML"] = True
            tc.cache_variables["USE_EXTERNAL_TINYXML"] = True
            tc.cache_variables["USE_EXTERNAL_LCMS"] = True

        tc.cache_variables["OCIO_USE_SSE"] = self.options.get_safe("use_sse", False)

        if self.dependencies["openexr"].ref.version < "3.0.0":   
            # openexr 2.x provides Half library
            tc.cache_variables["OCIO_USE_OPENEXR_HALF"] = True
        else:
            tc.cache_variables["OCIO_USE_OPENEXR_HALF"] = False

        tc.cache_variables["OCIO_BUILD_APPS"] = True
        tc.cache_variables["OCIO_BUILD_DOCS"] = False
        tc.cache_variables["OCIO_BUILD_TESTS"] = False
        tc.cache_variables["OCIO_BUILD_GPU_TESTS"] = False

        # avoid downloading dependencies
        tc.cache_variables["OCIO_INSTALL_EXT_PACKAGE"] = "NONE"

        if is_msvc(self) and not self.options.shared:
            # define any value because ifndef is used
            tc.cache_variables["OpenColorIO_SKIP_IMPORTS"] = True
        tc.generate()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        if not self.options.shared:
            copy(self, pattern="*", src=os.path.join(self.package_folder,
                      "lib", "static"), dst="lib")
            rmdir(self, os.path.join(self.package_folder, "lib", "static"))

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        # nop for 2.x
        rm(self, folder=self.package_folder, pattern="OpenColorIOConfig*.cmake", recursive=True)

        rm(self, folder=os.path.join(self.package_folder, "bin"), pattern="*.pdb", recursive=True)

        copy(self, "LICENSE", src=self.source_folder, dst="licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenColorIO")
        self.cpp_info.set_property("cmake_target_name", "OpenColorIO::OpenColorIO")
        self.cpp_info.set_property("pkg_config_name", "OpenColorIO")

        self.cpp_info.libs = ["OpenColorIO"]

        if Version(self.version) < "2.1.0":
            if not self.options.shared:
                self.cpp_info.defines.append("OpenColorIO_STATIC")

        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["Foundation", "IOKit", "ColorSync", "CoreGraphics"])

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("OpenColorIO_SKIP_IMPORTS")
            self.cpp_info.system_libs = ["gdi32"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenColorIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenColorIO"
        self.cpp_info.names["pkg_config"] = "OpenColorIO"
