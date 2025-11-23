vcpkg_from_github(
        OUT_SOURCE_PATH SOURCE_PATH
        REPO JonatanNevo/portal-framework
        REF 4a94c6ed75fd55a3a64b863a34463d28019816e8
        SHA512 81f0013b52ba4de49717fd2cd1a881bb2fbaf8c6e2d955311b051fcf0eb42b183c90541097453ea8adb32bbd9a1bac753aa10dbaee4aaeb24afd623a841c2137
        HEAD_REF fix/vcpkg-packaging
)

set(SOURCE_PATH "${SOURCE_PATH}/application")

vcpkg_cmake_configure(
        SOURCE_PATH "${SOURCE_PATH}"
        
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(
        PACKAGE_NAME portal-application
        CONFIG_PATH share/portal-application
)

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")

configure_file("${CMAKE_CURRENT_LIST_DIR}/usage" "${CURRENT_PACKAGES_DIR}/share/${PORT}/usage" COPYONLY)

vcpkg_copy_pdbs()