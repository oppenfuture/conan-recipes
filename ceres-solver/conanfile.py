import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

class ceressolverConan(ConanFile):
    name = "ceres-solver"
    version = "1.14.0"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://ceres-solver.org/r"
    description = ("Ceres Solver is an open source C++ library for modeling\
                    and solving large, complicated optimization problems")
    topics = ("optimization","Non-linear Least Squares")
    settings = "os", "arch", "compiler", "build_type"
    generators = ["cmake"]
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_glog":  [True, False],
               "use_gflags": [True, False],
               "use_custom_blas": [True, False],
               "use_eigen_sparse": [True, False],
               "use_TBB": [True, False],
               "use_CXX11_threads": [True, False],
               "use_CXX11": [True, False],
               "use_schur_specializations": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "use_glog": True,
                       "use_gflags": True,
                       "use_custom_blas": True,
                       "use_eigen_sparse": True,
                       "use_TBB": False,
                       "use_CXX11_threads": False,
                       "use_CXX11": False,
                       "use_schur_specializations": True}
    exports_sources = ["CMakeLists.txt","patches/*"]
    _source_subfolder = "source_subfolder"
    _cmake = None

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)       #You can check what these flags do in http://ceres-solver.org/installation.html
            self._cmake.definitions["GFLAGS"] = self.options.use_gflags
            self._cmake.definitions["BUILD_EXAMPLES"] = False           #Requires gflags
            self._cmake.definitions["BUILD_TESTING"] = False            #Requires gflags
            self._cmake.definitions["BUILD_DOCUMENTATION"] = False      #Requires python modules Sphinx and sphinx-rtd-theme
            self._cmake.definitions["CUSTOM_BLAS"] = self.options.use_custom_blas
            self._cmake.definitions["EIGEN_PREFER_EXPORTED_EIGEN_CMAKE_CONFIGURATION"] = False    #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["GLOG_PREFER_EXPORTED_GLOG_CMAKE_CONFIGURATION"] = False      #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["GFLAGS_PREFER_EXPORTED_GFLAGS_CMAKE_CONFIGURATION"] = False  #Set to false to Force CMake to use the conan-generated dependencies
            self._cmake.definitions["EIGENSPARSE"] = self.options.use_eigen_sparse
            self._cmake.definitions["SUITESPARSE"] = True  # Use systemlib for suitesparse
            self._cmake.definitions["LAPACK"] = True       # Use systemlib for lapack
            self._cmake.definitions["OPENMP"] = True
            self._cmake.definitions["CXSPARSE"] = True     # Use system lib for cxsparse
            self._cmake.definitions["MINIGLOG"] = not self.options.use_glog
            self._cmake.definitions["TBB"] = self.options.use_TBB
            self._cmake.definitions["CXX11_THREADS"] = self.options.use_CXX11_threads
            self._cmake.definitions["CXX11"] = self.options.use_CXX11
            self._cmake.definitions["SCHUR_SPECIALIZATIONS"] = self.options.use_schur_specializations
            if self.settings.os == "Windows":
                self._cmake.definitions["MSVC_USE_STATIC_CRT"] = str(self.settings.compiler.runtime) == "MT" or str(self.settings.compiler.runtime) == "MTd"
            self._cmake.configure()
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        if self.settings.build_type == "Debug" and self.options.use_glog:
            raise ConanInvalidConfiguration("Ceres-solver only links against the release version of glog")
        if self.options.use_glog and not self.options.use_gflags: #At this stage we can't check the value of self.options["glog"].with_gflags so we asume it is true because is the default value
            raise ConanInvalidConfiguration("To depend on glog built with gflags (Default behavior) set use_gflags=True, otherwise Ceres may fail to link due to missing gflags symbols.")

    def requirements(self):
        self.requires.add("eigen/3.2.10@oppen/testing")
        if self.options.use_glog:
            self.requires.add("glog/0.4.0")
        if self.options.use_gflags:
            self.requires.add("gflags/2.2.2")
        if self.options.use_TBB:
            self.requires.add("tbb/2020.0")

    def source(self):
        tools.get(url="https://github.com/ceres-solver/ceres-solver/archive/1.14.0.tar.gz", sha256="1296330fcf1e09e6c2f926301916f64d4a4c5c0ff12d460a9bc5d4c48411518f")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #Make sure that cmake finds gflags is use_gflags=True
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "find_package(Gflags)",
                              "find_package(Gflags REQUIRED)")
        #On windows the library names can be gflags.dll or gflags_static.lib
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "FindGflags.cmake"),
                              "find_library(GFLAGS_LIBRARY NAMES gflags",
                              "find_library(GFLAGS_LIBRARY NAMES gflags gflags_static")
        tools.patch(patch_file="patches/find-libraries-conan.patch", base_path="source_subfolder")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "CMake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include",os.path.join("include","ceres")]
        self.cpp_info.system_libs = [
            "cholmod",
            "ccolamd",
            "camd",
            "colamd",
            "amd",
            "suitesparseconfig",
            "rt",
            "cxsparse",
            "lapack",
            "blas",
            "f77blas",
            "atlas",
            "gomp",
            "pthread"
        ]
