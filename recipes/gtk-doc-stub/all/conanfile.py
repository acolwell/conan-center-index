from conan import ConanFile
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import unix_path
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
import functools
import os

required_conan_version = ">=1.33.0"


class GtkDocStubConan(ConanFile):
    name = "gtk-doc-stub"
    homepage = "https://gitlab.gnome.org/GNOME/gtk-doc-stub"
    description = "Helper scripts for generating GTK documentation"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-2.0-or-later"
    topics = ("gtk", "documentation", "gtkdocize")
    settings = "os"

    def build_requirements(self):
        if getattr(self, "settings_build", self.settings).os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.build_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self)

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = Autotools(self)
        args = [
            "--datadir={}".format(unix_path(self, os.path.join(self.package_folder, "res"))),
            "--datarootdir={}".format(unix_path(self, os.path.join(self.package_folder, "res"))),
        ]
        autotools.configure(args=args)
        return autotools

    def generate(self):
        ms = VirtualBuildEnv(self)
        ms.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        # Clear lib and bin directory info since this is a header-only package.
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        #automake_dir = unix_path(self, os.path.join(self.package_folder, "res", "aclocal"))
        #self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(automake_dir))
        #self.env_info.AUTOMAKE_CONAN_INCLUDES.append(automake_dir)
