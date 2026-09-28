# pylibfranka-macos

Unofficial macOS build of [pylibfranka](https://github.com/frankarobotics/libfranka), the Python bindings for libfranka, from [younghyopark/libfranka](https://github.com/younghyopark/libfranka/tree/macos-support), a fork with macOS support.

**This package is not affiliated with or endorsed by Franka Robotics GmbH.** On Linux, use the official [pylibfranka](https://pypi.org/project/pylibfranka/).

## Installation

```bash
pip install pylibfranka-macos
```

It needs an Apple Silicon Mac with macOS 15 or newer and Python 3.10 to 3.14. The wheels bundle their native dependencies, such as Poco, pinocchio and Boost, so they need no Homebrew.

The package installs the same `pylibfranka` module as the official package, so do not install both into one environment:

```python
import pylibfranka

robot = pylibfranka.Robot("172.16.0.2")
```

See the [pylibfranka documentation](https://frankarobotics.github.io/libfranka/pylibfranka/latest) for the API.

## Changes from libfranka

- Build on macOS.
- Busy-wait for robot states in a thread with the QoS class `USER_INTERACTIVE` instead of sleeping between control cycles. A thread that sleeps is often woken on an efficiency core or a clocked-down core, which slows down the following cycle several times and makes the robot drop commands. Set the environment variable `LIBFRANKA_MACOS_BUSY_WAIT=0` to sleep in a Mach time constraint thread instead.
- Detect TCP connections that the robot closed, which macOS reports differently from Linux.
- Do not hang when cancelling a motion that already ended, for example with `Robot.stop()`.

## Real-time notes

macOS is not a real-time operating system. Busy-waiting keeps one performance core fully busy while a control loop runs, so plug in the Mac when controlling the robot. Only the thread that creates the `Robot` gets the highest scheduling priority, so run the control loop on that thread. Connect the robot via wired Ethernet and watch `RobotState.control_command_success_rate` to check that your setup keeps up with the 1 kHz control loop.

## License

Apache-2.0, like libfranka. Each wheel includes the license and notice of libfranka and the licenses of the bundled libraries in its `.dist-info/licenses` directory.
