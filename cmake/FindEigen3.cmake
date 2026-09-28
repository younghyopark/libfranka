find_package(Eigen3 CONFIG)
mark_as_advanced(FORCE Eigen3_DIR)

# Eigen 5 no longer sets EIGEN3_INCLUDE_DIRS and only exports the Eigen3::Eigen target.
if(NOT EIGEN3_INCLUDE_DIRS AND TARGET Eigen3::Eigen)
  get_target_property(EIGEN3_INCLUDE_DIRS Eigen3::Eigen INTERFACE_INCLUDE_DIRECTORIES)
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Eigen3
  FOUND_VAR Eigen3_FOUND
  REQUIRED_VARS EIGEN3_INCLUDE_DIRS
)

if(NOT TARGET Eigen3::Eigen3)
  add_library(Eigen3::Eigen3 INTERFACE IMPORTED)
  set_target_properties(Eigen3::Eigen3 PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${EIGEN3_INCLUDE_DIRS}
    INTERFACE_COMPILE_DEFINITIONS "${EIGEN3_DEFINITIONS}"
  )
endif()
