from tkinter import *
import threading
import time

# Optional deps for inference/display
import numpy as np

# Try lightweight tflite runtime first; fallback to TF's bundled tflite
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_Interpreter = tflite.Interpreter
except Exception:
    from tensorflow.lite import Interpreter as TFLITE_Interpreter  # type: ignore

# Webcam (optional). If OpenCV is not installed, the app will still run.
try:
    import cv2
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False


class StudyTimer():
    def __init__(self):
        # ==== Tkinter UI ====
        self.root = Tk()
        self.root.title("Study Timer")
        self.root.config(padx=20, pady=20, bg="#f7f5dd")
        self.root.geometry("1000x700")

        # Top title
        self.title_label = Label(self.root, text="AI Study Timer", font=("Helvetica", 22, "bold"), bg="#f7f5dd")
        self.title_label.pack(pady=(0, 10))

        # Status line
        self.status_var = StringVar(value="Model: not loaded")
        self.status_label = Label(self.root, textvariable=self.status_var, font=("Helvetica", 12), bg="#f7f5dd")
        self.status_label.pack(pady=(0, 10))

        # Prediction line
        self.pred_var = StringVar(value="Prediction: -")
        self.pred_label = Label(self.root, textvariable=self.pred_var, font=("Helvetica", 16, "bold"), bg="#f7f5dd")
        self.pred_label.pack(pady=(0, 10))

        # Control buttons
        btn_frame = Frame(self.root, bg="#f7f5dd")
        btn_frame.pack(pady=10)
        self.load_btn = Button(btn_frame, text="Load TFLite Model", command=self.load_model)
        self.load_btn.grid(row=0, column=0, padx=5)
        self.start_btn = Button(btn_frame, text="Start Inference", state=DISABLED, command=self.start_inference)
        self.start_btn.grid(row=0, column=1, padx=5)
        self.stop_btn = Button(btn_frame, text="Stop", state=DISABLED, command=self.stop_inference)
        self.stop_btn.grid(row=0, column=2, padx=5)

        # If OpenCV available, allow camera toggle
        if _HAS_CV2:
            self.cam_btn = Button(btn_frame, text="Open Camera", command=self.toggle_camera)
            self.cam_btn.grid(row=0, column=3, padx=5)
        else:
            self.cam_btn = None

        # ==== Inference state ====
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.input_shape = None  # (1, H, W, C)
        self.input_dtype = None
        self.labels = self._load_labels_if_any("labels.txt")  # optional

        # Camera state
        self.cap = None
        self.camera_open = False

        # Loop control
        self._running = False

        # Graceful close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------- Model ----------
    def load_model(self, model_path: str = "model.tflite"):
        try:
            self.interpreter = TFLITE_Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.input_shape = self.input_details[0]['shape']  # e.g., [1, 224, 224, 3]
            self.input_dtype = self.input_details[0]['dtype']
            self.status_var.set(f"Model loaded: {model_path} | input={tuple(self.input_shape)} {self.input_dtype}")
            self.start_btn.config(state=NORMAL)
        except Exception as e:
            self.status_var.set(f"Failed to load model: {e}")

    def _load_labels_if_any(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [x.strip() for x in f.readlines() if x.strip()]
                return lines if lines else None
        except Exception:
            return None

    # ---------- Camera ----------
    def toggle_camera(self):
        if not _HAS_CV2:
            self.status_var.set("OpenCV not available. Install opencv-python to use camera.")
            return
        if self.camera_open:
            self._close_camera()
        else:
            self._open_camera()

    def _open_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError("Camera not found")
            self.camera_open = True
            self.cam_btn.config(text="Close Camera")
            self.status_var.set("Camera: opened")
        except Exception as e:
            self.status_var.set(f"Camera error: {e}")

    def _close_camera(self):
        try:
            if self.cap is not None:
                self.cap.release()
            self.cap = None
            self.camera_open = False
            if self.cam_btn:
                self.cam_btn.config(text="Open Camera")
            self.status_var.set("Camera: closed")
        except Exception as e:
            self.status_var.set(f"Camera close error: {e}")

    # ---------- Inference Loop ----------
    def start_inference(self):
        if self.interpreter is None:
            self.status_var.set("Load a TFLite model first.")
            return
        self._running = True
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.status_var.set("Inference: running")
        # Use Tkinter's after() to keep UI responsive
        self.root.after(50, self._inference_step)

    def stop_inference(self):
        self._running = False
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.status_var.set("Inference: stopped")

    def _inference_step(self):
        if not self._running:
            return

        # 1) Acquire input
        frame = None
        if _HAS_CV2 and self.camera_open and self.cap is not None:
            ok, frame = self.cap.read()
            if not ok:
                frame = None

        # 2) Build input tensor
        try:
            inp = self._prepare_input(frame)
        except Exception as e:
            self.pred_var.set(f"Preparation error: {e}")
            # Try again on next tick
            self.root.after(100, self._inference_step)
            return

        # 3) Run inference
        try:
            self.interpreter.set_tensor(self.input_details[0]['index'], inp)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        except Exception as e:
            self.pred_var.set(f"Invoke error: {e}")
            self.root.after(100, self._inference_step)
            return

        # 4) Post-process & display
        try:
            pred_text = self._format_prediction(output_data)
            self.pred_var.set(pred_text)
        except Exception as e:
            self.pred_var.set(f"Postprocess error: {e}")

        # 5) Schedule next step
        self.root.after(100, self._inference_step)

    def _prepare_input(self, frame):
        """
        Convert input (camera frame or fallback) to tensor with the model's expected shape & dtype.
        - If frame is None, feed zeros of correct shape (useful for testing).
        - Assumes NHWC input.
        """
        if self.input_shape is None or self.input_dtype is None:
            raise RuntimeError("Model not loaded")

        b, h, w, c = self.input_shape
        if frame is None:
            arr = np.zeros((b, h, w, c), dtype=self.input_dtype)
            return arr

        if not _HAS_CV2:
            raise RuntimeError("OpenCV not available but camera requested")

        # Convert BGR->RGB and resize
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (w, h), interpolation=cv2.INTER_LINEAR)
        arr = np.asarray(frame_resized)
        arr = np.expand_dims(arr, axis=0)  # (1, H, W, C)

        # Normalize/quantize according to dtype
        if self.input_dtype == np.float32:
            arr = arr.astype(np.float32) / 255.0
        else:
            # uint8 quantized model
            arr = arr.astype(self.input_dtype)
        return arr

    def _format_prediction(self, output_data: np.ndarray) -> str:
        """Return a nice text for UI. Supports common shapes: (1, N) or (1,).
        If labels.txt exists, map argmax to label name.
        """
        if output_data is None:
            return "Prediction: -"

        out = np.array(output_data)
        if out.ndim == 2 and out.shape[0] == 1:
            out = out[0]

        # Softmax-like normalization for readability, if floats
        if out.dtype.kind in {"f"}:
            # avoid overflow
            ex = np.exp(out - np.max(out))
            probs = ex / (np.sum(ex) + 1e-8)
        else:
            # For quantized outputs, just cast to float
            probs = out.astype(np.float32)
            s = probs.sum()
            if s > 0:
                probs = probs / s

        idx = int(np.argmax(probs)) if probs.ndim > 0 else 0
        conf = float(probs[idx]) if probs.ndim > 0 else 0.0

        if self.labels and 0 <= idx < len(self.labels):
            label = self.labels[idx]
        else:
            label = f"class_{idx}"
        return f"Prediction: {label} ({conf:.2f})"

    # ---------- Cleanup ----------
    def _on_close(self):
        self._running = False
        self._close_camera()
        try:
            # Release TFLite interpreter (optional)
            self.interpreter = None
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    study_timer = StudyTimer()
    study_timer.root.mainloop()