import json
import subprocess
import sys

import cv2


def detect_cameras(max_devices=8): # 사용 가능한 카메라 감지
    system_names = get_system_camera_names()
    cameras = []

    for index in range(max_devices):
        cap = cv2.VideoCapture(index)
        if cap is not None and cap.isOpened():
            name = system_names[index] if index < len(system_names) else f"Camera {index}"
            cameras.append((index, name))
        if cap is not None:
            cap.release()

    return cameras


def get_system_camera_names(): # 운영체제별 카메라 이름 조회
    names = []
    platform_key = sys.platform

    try:
        if platform_key == "darwin":
            output = subprocess.check_output([
                "system_profiler",
                "SPCameraDataType",
                "-json"
            ], text=True)
            data = json.loads(output)
            for camera in data.get("SPCameraDataType", []):
                name = camera.get("_name")
                if name:
                    names.append(name)
        elif platform_key.startswith("win"):
            command = [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_PnPEntity | Where-Object { $_.ClassGuid -eq '{ca3e7ab9-b4c3-4ae6-8251-579ef933890f}' } | Select-Object -ExpandProperty Name"
            ]
            output = subprocess.check_output(command, encoding="utf-8", errors="ignore")
            for line in output.splitlines():
                cleaned = line.strip()
                if cleaned:
                    names.append(cleaned)
        elif platform_key.startswith("linux"):
            output = subprocess.check_output(["v4l2-ctl", "--list-devices"], text=True)
            for line in output.splitlines():
                if line.strip() and not line.startswith("\t"):
                    names.append(line.split("(")[0].strip())
    except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
        pass

    return names


def get_camera_display_name(available_cameras, index): # 인덱스로 표시 이름 찾기
    for camera_index, camera_name in available_cameras:
        if camera_index == index:
            return camera_name
    return f"Camera {index}"
