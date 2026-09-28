// Copyright (c) 2023 Franka Robotics GmbH
// Use of this source code is governed by the Apache-2.0 license, see LICENSE
#include <franka/control_tools.h>

#include <cstring>
#include <exception>
#include <fstream>
#include <string>

#include "platform.h"

#ifdef LIBFRANKA_WINDOWS
#include <Windows.h>
#elif defined(LIBFRANKA_MACOS)
#include <mach/mach.h>
#include <mach/mach_error.h>
#include <mach/mach_time.h>
#include <mach/thread_policy.h>
#include <pthread.h>
#else
#include <pthread.h>
#endif

// `using std::string_literals::operator""s` produces a GCC warning that cannot be disabled, so we
// have to use `using namespace ...`.
// See https://gcc.gnu.org/bugzilla/show_bug.cgi?id=65923#c0
using namespace std::string_literals;  // NOLINT(google-build-using-namespace)

namespace franka {

bool hasRealtimeKernel() {
#if defined(LIBFRANKA_WINDOWS) || defined(LIBFRANKA_MACOS)
  return true;
#else
  std::ifstream realtime("/sys/kernel/realtime", std::ios_base::in);
  bool is_realtime{};
  realtime >> is_realtime;
  return is_realtime;
#endif
}

bool setCurrentThreadToHighestSchedulerPriority(std::string* error_message) {
#ifdef LIBFRANKA_WINDOWS
  auto get_last_windows_error = []() -> std::string {
    DWORD error_id = GetLastError();
    LPSTR buffer = nullptr;
    size_t size = FormatMessageA(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr, error_id, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)(&buffer), 0, nullptr);
    return std::string(buffer, size);
  };

  if (!SetPriorityClass(GetCurrentProcess(), REALTIME_PRIORITY_CLASS)) {
    if (error_message != nullptr) {
      *error_message =
          "libfranka: unable to set priority for the process: "s + get_last_windows_error();
    }
    return false;
  }

  if (!SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)) {
    if (error_message != nullptr) {
      *error_message =
          "libfranka: unable to set priority for the thread: "s + get_last_windows_error();
    }
    return false;
  }

  return true;
#elif defined(LIBFRANKA_MACOS)
  // SCHED_FIFO on macOS only raises the priority within the timeshare band. Real-time scheduling
  // requires the Mach time constraint policy, parametrized for the 1 kHz control cycle.
  constexpr uint64_t kPeriodNs = 1'000'000;
  constexpr uint64_t kComputationNs = 500'000;

  mach_timebase_info_data_t timebase{};
  kern_return_t result = mach_timebase_info(&timebase);
  if (result != KERN_SUCCESS) {
    if (error_message != nullptr) {
      *error_message = "libfranka: unable to get mach timebase: "s + mach_error_string(result);
    }
    return false;
  }
  auto to_absolute_time = [&timebase](uint64_t nanoseconds) {
    return static_cast<uint32_t>(nanoseconds * timebase.denom / timebase.numer);
  };

  thread_time_constraint_policy_data_t policy{};
  policy.period = to_absolute_time(kPeriodNs);
  policy.computation = to_absolute_time(kComputationNs);
  policy.constraint = to_absolute_time(kPeriodNs);
  policy.preemptible = 1;

  result = thread_policy_set(pthread_mach_thread_np(pthread_self()), THREAD_TIME_CONSTRAINT_POLICY,
                             reinterpret_cast<thread_policy_t>(&policy),
                             THREAD_TIME_CONSTRAINT_POLICY_COUNT);
  if (result != KERN_SUCCESS) {
    if (error_message != nullptr) {
      *error_message = "libfranka: unable to set realtime scheduling: "s + mach_error_string(result);
    }
    return false;
  }
  return true;
#else
  const int thread_priority = sched_get_priority_max(SCHED_FIFO);
  if (thread_priority == -1) {
    if (error_message != nullptr) {
      *error_message =
          "libfranka: unable to get maximum possible thread priority: "s + std::strerror(errno);
    }
    return false;
  }

  sched_param thread_param{};
  thread_param.sched_priority = thread_priority;
  if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &thread_param) != 0) {
    if (error_message != nullptr) {
      *error_message = "libfranka: unable to set realtime scheduling: "s + std::strerror(errno);
    }
    return false;
  }
  return true;
#endif
}

}  // namespace franka
