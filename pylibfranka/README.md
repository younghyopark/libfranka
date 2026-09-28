# pylibfranka Installation and Usage Guide

This document provides comprehensive instructions for installing and using pylibfranka, a Python binding for libfranka that enables control of Franka Robotics robots.

## Table of Contents
- [Installation](#installation)
  - [From PyPI (Recommended)](#from-pypi-recommended)
  - [From Source](#from-source)
- [Examples](#examples)
  - [Joint Position Example](#joint-position-example)
  - [Print Robot State Example](#print-robot-state-example)
  - [Joint Impedance Control Example](#joint-impedance-control-example)
  - [Gripper Control Example](#gripper-control-example)
- [Troubleshooting](#troubleshooting)

## Installation

### From PyPI (Recommended)

The easiest way to install pylibfranka is via pip. Pre-built wheels include all necessary dependencies.

```bash
pip install pylibfranka
```

#### Platform Compatibility

| Ubuntu Version | Supported Python Versions |
|----------------|---------------------------|
| 20.04 (Focal)  | Python 3.9 only           |
| 22.04 (Jammy)  | Python 3.9, 3.10, 3.11, 3.12 |
| 24.04 (Noble)  | Python 3.9, 3.10, 3.11, 3.12 |

**Note:** Ubuntu 20.04 users must use Python 3.9 due to glibc compatibility requirements.

### From Source

If you need to build from source (e.g., for development or unsupported platforms):

#### Prerequisites

- Python 3.9 or newer
- CMake 3.16 or newer
- C++ compiler with C++17 support
- Eigen3 development headers
- Poco development headers

**Disclaimer: If you are using the provided devcontainer, you can skip the prerequisites installation as they are already included in the container.**

#### Installing Prerequisites on Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake libeigen3-dev libpoco-dev python3-dev
```

#### Installing Prerequisites on macOS

pylibfranka can be built from source on macOS (Apple Silicon). There are no pre-built wheels for macOS, and the installed pylibfranka links against the Homebrew packages below at runtime, so keep them installed.

1. Install the Xcode Command Line Tools, which provide the C++ compiler:

   ```bash
   xcode-select --install
   ```

2. Install the dependencies with [Homebrew](https://brew.sh):

   ```bash
   brew install cmake pinocchio poco eigen console_bridge tinyxml2 fmt
   ```

   | Package | Used for |
   |---------|----------|
   | `pinocchio` | Robot model (kinematics and dynamics); also installs `urdfdom`, `boost` and `coal` |
   | `poco` | Network communication with the robot |
   | `eigen` | Linear algebra |
   | `console_bridge`, `tinyxml2` | URDF parsing |
   | `fmt` | Logging |
   | `cmake` | Build system |

3. Clone the repository including its submodules and continue with [Build and Install](#build-and-install), inside an activated conda environment or virtualenv:

   ```bash
   git clone --recurse-submodules -b macos-support https://github.com/younghyopark/libfranka.git
   ```

   Alternatively, install directly without cloning:

   ```bash
   pip install "git+https://github.com/younghyopark/libfranka@macos-support#subdirectory=pylibfranka"
   ```

Notes for macOS:

- If `brew upgrade` moves one of these packages to a new major version, `import pylibfranka` fails until you rebuild it with `pip install --force-reinstall --no-cache-dir .` (or the `git+https://...` URL above).
- If the conda `base` environment is on your `PATH` (for example when installing into `base` itself), its `fmt` package conflicts with Homebrew's and the build fails at link time. Use a separate environment, or prefix the `pip install` and `cmake` commands with `CMAKE_PREFIX_PATH=/opt/homebrew`.
- macOS is not a real-time operating system. To keep up with the 1 kHz control loop, libfranka busy-waits for robot states on macOS instead of sleeping between control cycles. This keeps one performance core fully busy while a control loop runs and drains the battery faster, so plug in the Mac when controlling the robot. The thread that creates the `Robot` gets the highest scheduling priority, so run the control loop on that thread. Set `LIBFRANKA_MACOS_BUSY_WAIT=0` to sleep between control cycles instead, at the cost of more missed cycles.
- Connect the robot via wired Ethernet and check with libfranka's `communication_test` example that your setup keeps up with the 1 kHz control loop. From the repository root:

  ```bash
  cmake -B build -DCMAKE_BUILD_TYPE=Release
  cmake --build build -j
  ./build/examples/communication_test <robot_ip>
  ```

#### Build and Install

From the `pylibfranka/` folder, you can install `pylibfranka` using pip:

```bash
pip install .
```

This will install pylibfranka in your current Python environment.

## Examples

pylibfranka comes with three example scripts that demonstrate how to use the library to control a Franka robot.

### Joint Position Example

This example demonstrates how to use an external control loop with pylibfranka to move the robot joints.

To run the example:

```bash
cd examples
python3 joint_position_example.py --ip <robot_ip>
```

Where `<robot_ip>` is the IP address of your Franka robot. If not specified, it defaults to "localhost".

The active control example:
- Sets collision behavior parameters
- Starts joint position control with CartesianImpedance controller mode
- Moves the robot using an external control loop
- Performs a simple motion of selected joints

### Print Robot State Example

This example shows how to read and display the complete state of the robot.

To run the example:

```bash
cd examples
python3 print_robot_state.py --ip <robot_ip> [--rate <rate>] [--count <count>]
```

Where:
- `--ip` is the robot's IP address (defaults to "localhost")
- `--rate` is the frequency at which to print the state in Hz (defaults to 0.5)
- `--count` is the number of state readings to print (defaults to 1, use 0 for continuous)

The print robot state example:
- Connects to the robot
- Reads the complete robot state
- Prints detailed information about:
  - Joint positions, velocities, and torques
  - End effector pose and velocities
  - External forces and torques
  - Robot mode and error states
  - Mass and inertia properties

### Joint Impedance Control Example

This example demonstrates how to implement a joint impedance controller that renders a spring-damper system to move the robot through a sequence of target joint configurations.

To run the example:

```bash
cd examples
python3 joint_impedance_example.py --ip <robot_ip>
```

Where `--ip` is the robot's IP address (defaults to "localhost").

The joint impedance example:
- Implements a minimum jerk trajectory generator for smooth joint motion
- Uses a spring-damper system for compliant control
- Moves through a sequence of predefined joint configurations:
  - Home position (slightly bent arm)
  - Extended arm pointing forward
  - Arm pointing to the right
  - Arm pointing to the left
  - Return to home position
- Includes position holding with dwell time between movements
- Compensates for Coriolis effects

### And more control examples

There are more control examples to discover. All of them can be executed in a similar way:

```bash
cd examples
python3 other_example.py --ip <robot_ip>
```

### Gripper Control Example

This example demonstrates how to control the Franka gripper, including homing, grasping, and reading gripper state.

To run the example:

```bash
cd examples
python3 move_gripper.py --robot_ip <robot_ip> [--width <width>] [--homing <0|1>] [--speed <speed>] [--force <force>]
```

Where:
- `--robot_ip` is the robot's IP address (required)
- `--width` is the object width to grasp in meters (defaults to 0.005)
- `--homing` enables/disables gripper homing (0 or 1, defaults to 1)
- `--speed` is the gripper speed (defaults to 0.1)
- `--force` is the gripper force in N (defaults to 60)

The gripper example:
- Connects to the gripper
- Performs homing to estimate maximum grasping width
- Reads and displays gripper state including:
  - Current width
  - Maximum width
  - Grasp status
  - Temperature
  - Timestamp
- Attempts to grasp an object with specified parameters
- Verifies successful grasping
- Releases the object

### Async Joint Position Control Example

You can also use the async API to control the robot in a low-rate fashion, e.g. 50Hz.
This allows you to specify joint position setpoints without the need for a blocking loop.

```bash
cd examples
python3 async_position_control.py --ip <robot_ip> 
```

