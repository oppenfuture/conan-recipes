from conans import ConanFile, tools
from conans.model.version import Version
import os
from glob import glob


class EigenConan(ConanFile):
    name = "eigen"
    version = "3.2.10"
    url = "https://github.com/conan-community/conan-eigen"
    homepage = "http://eigen.tuxfamily.org"
    description = "Eigen is a C++ template library for linear algebra: matrices, vectors, \
                   numerical solvers, and related algorithms."
    license = "MPL-2.0"
    author = "Conan Community"
    topics = ("eigen", "algebra", "linear-algebra", "vector", "numerical")
    settings = "compiler"
    exports = "LICENSE"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        source_url = "https://gitlab.com/libeigen/eigen/-/archive/"
        sha256 = "0920cb60ec38de5fb509650014eff7cc6d26a097c7b38c7db4b1aa5df5c85042"
        tools.get("{0}/{1}/eigen-{1}.tar.gz".format(source_url, self.version), sha256=sha256)
        os.rename(glob("eigen-*")[0], self._source_subfolder)

    def package(self):
        unsupported_folder = os.path.join(self.package_folder, "include", "eigen3", "unsupported", "Eigen")
        eigen_folder = os.path.join(self.package_folder, "include", "eigen3", "Eigen")
        self.copy("COPYING.*", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst=eigen_folder, src=os.path.join(self._source_subfolder, "Eigen"))
        self.copy("*", dst=unsupported_folder, src=os.path.join(self._source_subfolder, "unsupported", "Eigen"))
        self.copy("signature_of_eigen3_matrix_library", dst=os.path.join("include", "eigen3"), src=self._source_subfolder)
        os.remove(os.path.join(eigen_folder, "CMakeLists.txt"))
        os.remove(os.path.join(unsupported_folder, "CMakeLists.txt"))
        os.rename(os.path.join(unsupported_folder, "src", "LevenbergMarquardt", "CopyrightMINPACK.txt"),
                               os.path.join(self.package_folder, "licenses", "CopyrightMINPACK.txt"))

    def package_info(self):
        self.cpp_info.name = "Eigen3"
        self.cpp_info.includedirs = ['include/eigen3', 'include/unsupported']
        # By default, Visual Studio always returns the value "199711L" for the __cplusplus preprocessor macro.
        # The /Zc:__cplusplus compiler option is available starting in Visual Studio 2017 version 15.7.
        # When /Zc:__cplusplus option is enabled, the value reported by the __cplusplus macro depends on the /std version switch setting.
        # References: https://docs.microsoft.com/en-us/cpp/build/reference/zc-cplusplus?view=vs-2019
        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version.value) >= "15":
            self.cpp_info.cxxflags.append("/Zc:__cplusplus")
