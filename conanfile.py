import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import unzip, check_sha256, copy, patch


required_conan_version = ">=2.00.00"
SOURCE_TAR_GZ_SHA256 = ("13f6924b2ed71df9b137a7df98706a0d"
                        "cc3b43c283a0e32f8b6eadca4305136a")

class IntelDfpPackage(ConanFile):
    name = "intel-dfp"
    version = "2.3"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"

    description = "Software decimal floating-point arithmetic implementation"
    homepage = ("https://www.intel.com/content/www/us/en/developer/articles/"
                "tool/intel-decimal-floating-point-math-library.html")
    url = "https://github.com/AlxndrMkrv/intel-dfp"
    license = ("MIT", "Intel")
    topics = ("decimal", "dfp", "ieee-754", "intel")

    options = {
        "shared": [True, False],
        "verbose": [True, False],
        "call_by_reference": [True, False],
        "global_rounding": [True, False],
        "global_exception": [True, False],
        "unchanged_binary_flags": [True, False]
    }
    default_options = {
        "shared": False,
        "verbose": False,
        "call_by_reference": False,
        "global_rounding": False,
        "global_exception": False,
        "unchanged_binary_flags": False
    }
     
    def source(self):
        tar_gz_name = os.path.join(self.export_sources_folder,
                                   "IntelRDFPMathLib20U3.tar.gz")
        check_sha256(self, tar_gz_name, SOURCE_TAR_GZ_SHA256)
        unzip(self, tar_gz_name)

        patch(self, patch_file="readtest.c.patch", strip=1)

        cmakelists_dst = os.path.join(self.source_folder, "CMakeLists.txt")
        if not os.path.isfile(cmakelists_dst):
            os.symlink(src=os.path.join(self.export_sources_folder,
                                        "CMakeLists.txt"),
                       dst=cmakelists_dst)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        self.folders.set_base_source("sources")
        cmake_layout(self, src_folder="sources")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.0 <4]")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["SHARED"] = self.options.shared
        tc.variables["CALL_BY_REF"] = self.options.call_by_reference
        tc.variables["GLOBAL_RND"] = \
            self.options.global_rounding
        tc.variables["GLOBAL_EXC"] = \
            self.options.global_exception
        tc.variables["INEXACT_FLAG"] = \
            not self.options.unchanged_binary_flags
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "eula.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def export_sources(self):
        copy(self, "CMakeLists.txt",
             os.path.join(self.recipe_folder, "sources"),
             self.export_sources_folder)
        copy(self, "IntelRDFPMathLib20U3.tar.gz",
             os.path.join(self.recipe_folder, "sources"),
             self.export_sources_folder)
        copy(self, "readtest.c.patch",
             os.path.join(self.recipe_folder, "patches"),
             self.export_sources_folder)

    def package_info(self):
        self.cpp_info.libs = ["intel_dfp"]
        self.cpp_info.set_property("cmake_file_name", "intel_dfp")
        self.cpp_info.set_property("cmake_target_name", "intel_dfp::intel_dfp")

        defs = {"DECIMAL_CALL_BY_REFERENCE": self.options.call_by_reference,
                "DECIMAL_GLOBAL_ROUNDING": self.options.global_rounding,
                "DECIMAL_GLOBAL_EXCEPTION_FLAGS": self.options.global_exception,
                "UNCHANGED_BINARY_FLAGS": self.options.unchanged_binary_flags}
        self.cpp_info.defines = [f"{k}={int(eval(v.value))}"
                                 for k, v in defs.items()]

        if self.settings.compiler in ("clang", "gcc"):
            self.cpp_info.defines.append("_WCHAR_T=__WCHAR_TYPE__")
        elif self.settings.compiler == "msvc":
            self.cpp_info.defines.append("_WCHAR_T=_NATIVE_WCHAR_T_DEFINED")
