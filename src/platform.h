// Copyright (c) 2023 Franka Robotics GmbH
// Use of this source code is governed by the Apache-2.0 license, see LICENSE
#pragma once

#undef LIBFRANKA_X64
#undef LIBFRANKA_X86
#undef LIBFRANKA_ARM64
#undef LIBFRANKA_ARM

#if defined(__amd64__) || defined(_M_AMD64)
#define LIBFRANKA_X64
#elif defined(__X86__) || defined(_M_IX86)
#define LIBFRANKA_X86
#elif defined(__aarch64__) || defined(_M_ARM64)
#define LIBFRANKA_ARM64
#elif defined(__arm__) || defined(_M_ARM)
#define LIBFRANKA_ARM
#endif

#undef LIBFRANKA_WINDOWS
#undef LIBFRANKA_MACOS
#undef LIBFRANKA_LINUX

#if defined(_WIN32) || defined(_WIN64)
#define LIBFRANKA_WINDOWS
#elif defined(__APPLE__) && defined(__MACH__)
#define LIBFRANKA_MACOS
#elif defined(__unix) || defined(__unix__)
#define LIBFRANKA_LINUX
#endif

#ifdef LIBFRANKA_MACOS
#include <cstdlib>
#include <cstring>

namespace franka {

/**
 * Whether to busy-wait for robot states on macOS.
 *
 * A thread that sleeps between control cycles is often woken on an efficiency core or a
 * clocked-down core, which slows down the following cycle several times. Therefore, libfranka
 * busy-waits for robot states in a USER_INTERACTIVE thread by default. Setting the environment
 * variable LIBFRANKA_MACOS_BUSY_WAIT=0 restores sleeping in a Mach time constraint thread, which
 * saves power but misses more control cycles.
 */
inline bool macosBusyWait() {
  const char* value = std::getenv("LIBFRANKA_MACOS_BUSY_WAIT");
  return value == nullptr || std::strcmp(value, "0") != 0;
}

}  // namespace franka
#endif
